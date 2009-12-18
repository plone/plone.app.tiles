from zope.interface import Interface, implements
from zope.component import queryMultiAdapter, queryUtility
from zope.component import getAllUtilitiesRegisteredFor

from zope.security import checkPermission
from zope.publisher.interfaces import IPublishTraverse

from plone.memoize.view import memoize

from plone.tiles.interfaces import ITileType
from plone.app.tiles.interfaces import ITileAddView, ITileEditView

from plone.app.tiles import MessageFactory as _

from Products.Five.browser import BrowserView

class TileTraverser(BrowserView):
    """Base class for tile add/edit view traversers.
    
    In effect, the add and edit view traversers do the same thing, they are
    just conceptually different. It is important to realise that you need to
    pass at least the `id` query string parameter to the traverser, and,
    in the case of the edit traverser for transient tiles, you'll also need
    to pass the existing tile query string.
    """

    targetInterface = Interface
    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def publishTraverse(self, request, name):
        """Allow traveral to @@<view>/tilename
        """
        
        tile_info = queryUtility(ITileType, name=name)
        if tile_info is None:
            raise KeyError(name)
        
        view = queryMultiAdapter((self.context, self.request, tile_info), self.targetInterface, name=name)
        if view is None:
            view = queryMultiAdapter((self.context, self.request, tile_info), self.targetInterface)
        
        if view is None:
            raise KeyError(name)
        
        view.__name__ = name
        view.__parent__ = self.context
        
        return view

class AddTile(TileTraverser):
    """Implements the @@add-tile traversal view
    
    Rendering this view on its own will display a template where the user
    may choose a tile type to add.
    
    Traversing to /path/to/obj/@@add-tile/@@tile-name?id=foo will:
    
        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return the view for rendering
    """

    targetInterface = ITileAddView

    def tileSortKey(self, type1, type2):
        return cmp(type1.title, type2.title)
    
    @memoize
    def tileTypes(self):
        """Get a list of addable ITileType objects representing tiles
        which are addable in the current context
        """
        types = []
        
        for type_ in getAllUtilitiesRegisteredFor(ITileType):
            if checkPermission(type_.add_permission, self.context):
                types.append(type_)
        
        types.sort(self.tileSortKey)
        return types
    
    def __call__(self):
        
        self.errors = {}
        self.request['disable_border'] = True
        
        if 'form.button.Create' in self.request:
            newTileType = self.request.get('type', None)
            newTileId = self.request.get('id', None)
            if newTileType is None:
                self.errors['type'] = _(u"You must select the type of tile to create")
            if newTileId is None:
                self.errors['id'] = _(u"You must specify an id")
            
            if len(self.errors) == 0:
                self.request.response.redirect("%s/@@add-tile/%s?id=%s" % \
                        (self.context.absolute_url(), newTileType, newTileId))
                return ''
            
        return self.index()

class EditTile(TileTraverser):
    """Implements the @@edit-tile namespace.
    
    Traversing to /path/to/obj/@@edit-tile/@@tile-name?id=foo will:
    
        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return the view for rendering
    """

    targetInterface = ITileEditView
    
    def __call__(self):
        raise KeyError("Please traverse to @@edit-tile/<tilename>?id=<id>")
