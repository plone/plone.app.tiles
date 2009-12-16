from zope.interface import implements, Interface
from zope.component import adapts, queryMultiAdapter, queryUtility

from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError

from zope.publisher.interfaces.browser import IBrowserRequest

from plone.tiles.interfaces import ITileType
from plone.app.tiles.interfaces import ITileAddView, ITileEditView

class TileTraverser(object):
    """Base class for tile add/edit view traversers.
    
    In effect, the add and edit view traversers do the same thing, they are
    just conceptually different. It is important to realise that you need to
    pass at least the `id` query string parameter to the traverser, and,
    in the case of the edit traverser for transient tiles, you'll also need
    to pass the existing tile query string.
    """

    implements(ITraversable)
    adapts(Interface, IBrowserRequest)
    
    targetInterface = Interface

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, further):
        
        tile_info = queryUtility(ITileType, name=name)
        if tile_info is None:
            raise TraversalError(self.context, name)
        
        view = queryMultiAdapter((self.context, self.request, tile_info), self.targetInterface, name=name)
        if view is None:
            view = queryMultiAdapter((self.context, self.request, tile_info), self.targetInterface)
        
        if view is None:
            raise TraversalError(self.context, name)
        
        view.__name__ = name
        view.__parent__ = self.context
        
        return view

class TileAddViewTraverser(TileTraverser):
    """Implements the ++addtile++ namespace.
    
    Traversing to /path/to/obj/++addtile++tile-name?id=foo will:
    
        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return the view for rendering
    """

    adapts(Interface, IBrowserRequest)
    
    targetInterface = ITileAddView


class TileEditViewTraverser(TileTraverser):
    """Implements the ++edittile++ namespace.
    
    Traversing to /path/to/obj/++edittile++tile-name?id=foo will:
    
        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return the view for rendering
    """

    adapts(Interface, IBrowserRequest)
    
    targetInterface = ITileEditView
