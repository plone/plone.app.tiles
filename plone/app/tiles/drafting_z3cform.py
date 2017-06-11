# -*- coding: utf-8 -*-
from plone.app.drafts.interfaces import ICurrentDraftManagement
from plone.app.drafts.interfaces import IDraftable
from plone.app.drafts.proxy import DraftProxy
from plone.app.tiles.drafting import draftingTileDataContext
from plone.app.tiles.interfaces import ITilesFormLayer
from plone.behavior.interfaces import IBehaviorAssignable
from plone.namedfile.scaling import ImageScaling
from plone.tiles.interfaces import ITile
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
    def __init__(self, context, request):
        referer = (request.get('HTTP_REFERER') or '').split('?', 1)[0]
        if referer and IDisplayFormDrafting.providedBy(request) and (
            referer.endswith('/edit') or
            referer.endswith('/@@edit') or
            referer.split('/')[-1].startswith('++add++')
        ):
            self._drafting = True
            ICurrentDraftManagement(request).mark()
            context = draftingTileDataContext(context, request, context)
        else:
            self._drafting = False
        super(TileDraftingImageScaling, self).__init__(context, request)

    def scale(
        self,
        fieldname=None,
        scale=None,
        height=None,
        width=None,
        direction='thumbnail',
        **parameters
    ):
        # Save drafted scales separately from other scales. With concurrent
        # drafts there may still be race condition.
        if self._drafting:
            # Currently the only option to differentiate draft cache key
            parameters['result'] = None
        return super(TileDraftingImageScaling, self).scale(
            fieldname=fieldname,
            scale=scale,
            height=height,
            width=width,
            direction=direction,
            **parameters
        )


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
