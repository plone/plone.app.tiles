from zope.interface import Interface, implements
from zope.component import queryMultiAdapter, queryUtility
from zope.component import getAllUtilitiesRegisteredFor

from zope.security import checkPermission
from zope.publisher.interfaces import IPublishTraverse

from plone.memoize.view import memoize

from plone.tiles.interfaces import ITileType

from plone.app.tiles.interfaces import ITileAddView, ITileEditView

from plone.app.tiles import MessageFactory as _


class TileTraverser(object):
    """Base class for tile add/edit view traversers.

    This is responsible for fetching the tile name and tile id out of a URL
    like ``.../@@traversal-view/my.tile.name/tile-id``.

    We then look up an adapter from ``(context, request, tileType)`` to an
    appropriate interface. The default is to use the unnamed adapter, but this
    can be overridden by registering a named adapter with the name of the
    tile type. This way, a custom add/edit view can be reigstered for a
    particular type of tile.

    The tile id is set onto the view that was looked up, as the ``tileId``
    attribute.

    Below, we register two traversal views: ``@@add-tile`` and
    ``@@edit-tile``.
    """

    targetInterface = Interface
    implements(IPublishTraverse)

    view = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getTileViewByName(self, tile_name):
        tile_info = queryUtility(ITileType, name=tile_name)
        if tile_info is None:
            raise KeyError(tile_name)

        view = queryMultiAdapter((self.context, self.request, tile_info),
                self.targetInterface, name=tile_name)

        if view is None:
            view = queryMultiAdapter((self.context, self.request, tile_info),
                    self.targetInterface)

        if view is None:
            raise KeyError(tile_name)

        view.__name__ = name
        view.__parent__ = self.context

        return view

class AddTile(TileTraverser):
    """Implements the @@add-tile traversal view

    Rendering this view on its own will display a template where the user
    may choose a tile type to add.

    Traversing to /path/to/obj/@@add-tile/tile-name will:

        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find view which is an adapter for (context, request,
            tile_info) with the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Return above found view for rendering
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
            if newTileType is None:
                self.errors['type'] = _(u"You must select the type of " + \
                                        u"tile to create")

            if len(self.errors) == 0:
                self.request.response.redirect("%s/@@add-tile/%s" % \
                        (self.context.absolute_url(), newTileType))
                return ''

        return self.index()

    def publishTraverse(self, request, name):
        """Allow traversal to @@<view>/tilename
        """

        # 1. Look up the view, but keep this view as the traversal context
        if self.view is None:
            self.view = self.getTileViewByName(name)
            return self.view

        raise KeyError(name)


class EditTile(TileTraverser):
    """Implements the @@edit-tile namespace.

    Traversing to /path/to/obj/@@edit-tile/tile-name/tile-id will:

        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Set the 'tileId' property on the view to the id 'tile-id
        * Return the view for rendering
    """

    targetInterface = ITileEditView

    def __call__(self):
        raise KeyError("Please traverse to @@edit-tile/tilename/id")

    def publishTraverse(self, request, name):
        """Allow traversal to @@<view>/tilename/tileid
        """

        # 1. Look up the view, but keep this view as the traversal context in
        # anticipation of an id
        if self.view is None:
            self.view = self.getTileViewByName(name)
            return self

        # 2. Set the id and return the view we looked up in the previous
        # traversal step.
        elif getattr(self.view, 'tileId', None) is None:
            self.view.tileId = name
            return self.view

        raise KeyError(name)


