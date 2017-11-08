# -*- coding: utf-8 -*-
from Acquisition import aq_base
from DateTime import DateTime
from plone.app.drafts.interfaces import ICurrentDraftManagement
from plone.app.drafts.interfaces import IDraftable
from plone.app.drafts.proxy import DraftProxy
from plone.app.tiles.drafting import draftingTileDataContext
from plone.app.tiles.interfaces import ITilesFormLayer
from plone.behavior.interfaces import IBehaviorAssignable
from plone.namedfile.scaling import ImageScaling
from plone.scale.storage import AnnotationStorage
from plone.tiles.interfaces import ITile
from plone.uuid.interfaces import IUUID
from plone.z3cform.traversal import FormWidgetTraversal
from z3c.form.field import FieldWidgets as FieldWidgetsBase
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IWidgets
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable
from ZPublisher.interfaces import IPubAfterTraversal

try:
    from plone.app.drafts.dexterity import IDisplayFormDrafting
except ImportError:
    class IDisplayFormDrafting(object):
        pass


class ITileDrafting(Interface):
    """Marker interface to be applied for tile views, when they should show
    draft instead of real context."""


@adapter(IPubAfterTraversal)
def afterTraversalDrafting(event):
    """Enable drafting for requests rendering tiles (mainly field tiles),
    when request's http refer hints that the request is being sent from an add
    form.

    Note: Because this is called before tile view initialization, it's enough
    to mark request with drafting marker. It will toggle forms on tile to
    be rendered with drafting support (e.g. DexterityFieldTile is based on
    rendering fields using z3c.form widgets in display mode).
    """
    request = event.request
    if not ITile.providedBy(request.get('PUBLISHED')):
        return
    referer = (request.get('HTTP_REFERER') or '').split('?', 1)[0]
    if (referer.split('/')[-1].startswith('++add++') or
            referer.endswith('/edit') or referer.endswith('/@@edit')):
        alsoProvides(request.get('PUBLISHED'), ITileDrafting)
        alsoProvides(request, IDisplayFormDrafting)


@implementer(ITraversable, IPublishTraverse)
class TileDraftingImageScaling(ImageScaling):
    """Enable drafting when a view using @@images is referred from
    edit view

    Note: This is ugly, because this overrides the default @@images, and
    drafted scales must be saved with the current scales to result in working
    image src URLs.

    Todo: It should be checked, if simply checking for the existence of
    _layouteditor-query could be enough for triggering drafting mode.
    """
    def __init__(self, context, request):
        self._context = context  # Save the original context
        referer = (request.get('HTTP_REFERER') or '').split('?', 1)[0]
        if referer and IDisplayFormDrafting.providedBy(request) and (
            referer.endswith('/edit') or
            referer.endswith('/@@edit') or
            referer.split('/')[-1].startswith('++add++')
        ):
            current = ICurrentDraftManagement(request)
            if current.path == '/'.join(context.getPhysicalPath()):
                current.mark()
                context = draftingTileDataContext(context, request, context)
                self._drafting = True
            else:
                self._drafting = False
        else:
            self._drafting = False
        super(TileDraftingImageScaling, self).__init__(context, request)

    def modified(self):
        # Modification date must be based on the original context or
        # image scale storage will be cleared because of too recent _p_mtime
        # of possible DraftProxy.
        context = aq_base(self._context)
        date = DateTime(context._p_mtime)
        return date.millis()

    def scale(
        self,
        fieldname=None,
        scale=None,
        height=None,
        width=None,
        direction='thumbnail',
        **parameters
    ):
        def create():
            return super(TileDraftingImageScaling, self).scale(
                fieldname=fieldname,
                scale=scale,
                height=height,
                width=width,
                direction=direction,
                **parameters
            )

        data = getattr(aq_base(self._context), fieldname, None)
        draft = getattr(aq_base(self.context), fieldname, None)

        if draft is None:
            return None

        view = create()

        # 1) When draft has no changes scale the original
        if data is draft:
            self._drafting = False

        # 2) For modified drafts, Save drafted scales separately from other
        # scales. (With concurrent drafts there may still be race condition.)
        if self._drafting:
            # Currently the only option to differentiate draft cache key by
            # setting the otherwise unused 'result' parameter to its default
            # value 'None'
            parameters['result'] = None
            view = create()

        # 3) If drafted data is newer than drafted scale, renew the scale:
        if self._drafting and view.data._p_mtime:
            if draft._p_mtime > view.data._p_mtime:
                storage = AnnotationStorage(self.context, self.modified)
                del storage[view.uid]
                view = create()

        # from datetime import datetime
        # print self.context
        # for value in self.context.__annotations__['plone.scale'].values():
        #     print value['uid'], datetime.fromtimestamp(
        #         value['modified'] / 1000.), value['key'][-2][-1]
        # print '-' * 80

        return view


@adapter(ITileDrafting, IDisplayFormDrafting, Interface)
@implementer(IWidgets)
class DisplayTileFormFieldWidgets(FieldWidgetsBase):
    def __init__(self, form, request, context):
        assignable = IBehaviorAssignable(context, None)
        if assignable is not None and assignable.supports(IDraftable):
            current = ICurrentDraftManagement(request)
            if current.targetKey is not None:
                current.mark()
            if current.draft:
                context = DraftProxy(current.draft, context)
        super(DisplayTileFormFieldWidgets, self).__init__(form, request, context)  # noqa


@implementer(ITraversable)
@adapter(IForm, ITilesFormLayer)
class TileWidgetTraversal(FormWidgetTraversal):
    """Enable drafting for requests rendering widgets below tiles using
    widget traversal (e.g. when rendering image field on field tile), when
    request's http refer hints that the request is being sent from an add form.

    Note: Because this is called only after initial tile view initialization,
    it's not enough to mark request with drafting marker, but we must set
    update widget's context with a DraftProxy.
    """

    def __init__(self, context, request=None):
        super(TileWidgetTraversal, self).__init__(context, request)
        referer = (self.request.get('HTTP_REFERER') or '').split('?', 1)[0]
        if referer and ITile.providedBy(context) and (
            referer.endswith('/edit') or
            referer.endswith('/@@edit') or
            referer.split('/')[-1].startswith('++add++')
        ):
            ICurrentDraftManagement(self.request).mark()
            self.context.context = draftingTileDataContext(
                context.context, request, context)
