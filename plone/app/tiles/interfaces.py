from zope.schema import TextLine
from zope.publisher.interfaces.browser import IBrowserView
from zope.i18nmessageid import MessageFactory
from plone.supermodel import model

_ = MessageFactory('plone')


class ITileAddView(IBrowserView):
    """A tile add view as found by the @@add-tile traversal view.

    The default add view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """


class ITileEditView(IBrowserView):
    """A tile add view as found by the @@edit-tile traversal view.

    The default edit view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """


class ITileBaseSchema(model.Schema):
    """ Base interfaces from which all Plone tiles should inherit.
    """

    # TODO: use some fieldset to put this into so its not on the first page
    # TODO: should classes be defined in line
    klass = TextLine(
        title=_(u"Additional classes."),
        required=False,
        )
