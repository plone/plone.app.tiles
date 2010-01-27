from zope.interface import Interface
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

class ITileBookkeeping(Interface):
    """Tile bookkeeping information.
    
    Adapt a content object to this interface to obtain information about tiles
    associated with that content item. The default implementation stores this
    information in annotations, and maintains it using event handlers for
    ``IObjectAddedEvent`` and ``IObjectRemovedEvent`` for ``ITile``.
    """
    
    def added(tileType, tileId):
        """Record that a tile of the given type (a string) and id (also a
        string) was added.
        """

    def removed(tileType, tileId):
        """Record that a tile with the given id (a string) was removed.
        """
    
    def typeOf(tileId):
        """Given a tile id, return its type (a strong), or None if the tile
        cannot be found.
        """
    
    def counter():
        """Get the number of tiles that have been added. Note that the counter
        is *not* decremented even if tiles are removed.
        """
    
    def enumerate(tileType=None):
        """Obtain an iterator for all tiles which have been recorded. The
        iterator returns tuples of strings ``(tileId, tileType)``. If
        ``tileType`` is given, return only tiles of that type.
        """
