from zope.publisher.interfaces.browser import IBrowserView

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
