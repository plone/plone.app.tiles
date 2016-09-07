# -*- coding: utf-8 -*-
from plone.app.tiles import _ as _
from plone.app.tiles.interfaces import ALLOWED_TILES_VOCABULARY
from plone.app.tiles.interfaces import ITileAddView
from plone.app.tiles.interfaces import ITileDeleteView
from plone.app.tiles.interfaces import ITileEditView
from plone.memoize.view import memoize
from plone.tiles.interfaces import ITileType
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory
from zope.security import checkPermission


class TileTraverser(object):
    """Base class for tile add/edit view traversers.

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
        """We look up for adapter from ``(context, request, tileType)`` to an
        appropriate interface. The default is to use the unnamed adapter, but
        this can be overridden by registering a named adapter with the name of
        the tile type. This way, a custom add/edit view can be registered for
        a particular type of tile.
        """

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

        view.__name__ = tile_name
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
        tiles = []

        factory = getUtility(IVocabularyFactory,
                             name=ALLOWED_TILES_VOCABULARY)
        vocabulary = factory(self.context)

        for item in vocabulary:
            tiletype = item.value
            # check if we have permission to add this tile
            if tiletype and checkPermission(
                    tiletype.add_permission, self.context):
                # tile actions
                # TODO: read from registry
                tiletype.actions = [{
                    'name': 'edit',
                    'url': '@@edit-tile',
                    'title': _('Edit'),
                }, {
                    'name': 'remove',
                    'url': '@@delete-tile',
                    'title': _('Remove'),
                }]
                tiles.append(tiletype)

        tiles.sort(self.tileSortKey)
        return tiles

    def __call__(self):
        self.errors = {}
        self.request['disable_border'] = True
        if 'form.button.Create' in self.request:
            newTileType = self.request.get('tiletype', None)
            if newTileType is None:
                self.errors['tiletype'] = _(u"You must select the type of " +
                                            u"tile to create")

            if len(self.errors) == 0:
                self.request.response.redirect("%s/@@add-tile/%s" % (
                    self.context.absolute_url(), newTileType))
                return ''

        return self.index()

    def publishTraverse(self, request, name):
        """Allow traversal to @@<view>/tilename."""

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


class DeleteTile(TileTraverser):
    """Implements the @@delete-tile traversal view

    Traversing to /path/to/obj/@@delete-tile/tile-name/tile-id will delete tile.
    """

    tileId = None
    targetInterface = ITileDeleteView

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tileId = None
        self.annotations = IAnnotations(self.context)

    def __call__(self):
        raise KeyError("Please traverse to @@delete-tile/tilename/id")

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
