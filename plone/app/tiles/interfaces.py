from zope.publisher.interfaces.browser import IBrowserView

class ITileAddView(IBrowserView):
    """A tile add view as found by the ++addtile++ traverser.
    
    The default add view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """

class ITileEditView(IBrowserView):
    """A tile add view as found by the ++edittile++ traverser.
    
    The default add view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """
