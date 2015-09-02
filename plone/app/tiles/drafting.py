# -*- coding: utf-8 -*-
from urlparse import urlparse

from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.blocks.utils import resolveResource
from plone.app.drafts.interfaces import ICurrentDraftManagement
from plone.app.drafts.interfaces import IDraft
from plone.app.drafts.interfaces import IDraftSyncer
from plone.app.drafts.interfaces import IDrafting
from plone.app.drafts.interfaces import USERID_KEY
from plone.app.drafts.proxy import DraftProxy
from plone.app.drafts.utils import getCurrentDraft
from plone.app.tiles.interfaces import ITilesFormLayer
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from plone.tiles.interfaces import ITile
from plone.tiles.interfaces import ITileDataContext
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implements


@implementer(ITileDataContext)
@adapter(Interface, ITilesFormLayer, ITile)
def draftingTileDataContext(context, request, tile):
    """If we are drafting a content item, record tile data information
    to the draft, but read existing data from the underlying object.
    """
    # When drafted content with tiles is saved, IDrafting is provided
    if IDrafting.providedBy(request):
        if request.method == 'POST':
            draft = getCurrentDraft(request, create=True)
        else:
            draft = getCurrentDraft(request, create=False)
        if draft is None:
            return context

    # When tile is previewed during drafted content is edited, heuristics...
    else:
        # Manually configure draft user id, if we are still in traverse
        if getattr(request, 'PUBLISHED', None) is None:
            IAnnotations(request)[USERID_KEY] = request.cookies.get(USERID_KEY)

        # No active draft for the request
        draft = getCurrentDraft(request)
        if draft is None:
            return context

        # Not referring from an edit form
        referrer = request.get('HTTP_REFERER', '')
        path = urlparse(referrer).path
        if all((not path.endswith('/edit'),
                not path.endswith('/@@edit'),
                not path.split('/')[-1].startswith('++add++'))):
            return context

        ICurrentDraftManagement(request).mark()

    return DraftProxy(draft, context)


class TileDataDraftSyncer(object):
    """Copy draft persistent tile data to the real object on save
    """

    implements(IDraftSyncer)
    adapts(IDraft, Interface)

    def __init__(self, draft, target):
        self.draft = draft
        self.target = target

    def __call__(self):

        draftAnnotations = IAnnotations(self.draft)
        targetAnnotations = IAnnotations(self.target)

        behavior_data = ILayoutAware(self.target)
        try:
            contentLayout = behavior_data.contentLayout
        except AttributeError:
            contentLayout = None
        if contentLayout:
            try:
                layout = resolveResource(behavior_data.contentLayout)
            except (NotFound, RuntimeError):
                layout = ''
        else:
            layout = behavior_data.content

        for key, value in draftAnnotations.iteritems():
            if key.startswith(ANNOTATIONS_KEY_PREFIX):
                tile_id = key[len(ANNOTATIONS_KEY_PREFIX) + 1:]
                if tile_id in layout:
                    targetAnnotations[key] = value

        annotationsDeleted = getattr(
            self.draft, '_proxyAnnotationsDeleted', set())

        for key in annotationsDeleted:
            if key.startswith(ANNOTATIONS_KEY_PREFIX) and key in targetAnnotations:  # noqa
                del targetAnnotations[key]

        # TODO: Should we also remove all tile annotations, whose tile_id
        # cannot be found from layout?
