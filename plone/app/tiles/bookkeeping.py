"""Event handlers to keep a list of tiles
"""

from zope.interface import implements

from zope.component import adapts
from zope.component import adapter
from zope.component import getMultiAdapter

from zope.annotation.interfaces import IAnnotatable, IAnnotations

from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from plone.tiles.interfaces import ITile
from plone.tiles.interfaces import ITileDataContext

from plone.app.tiles.interfaces import ITileBookkeeping

ANNOTATIONS_KEY = "plone.app.tiles.bookkeeping"
COUNTER_KEY = "plone.app.tiles.counter"

@adapter(ITile, IObjectAddedEvent)
def recordTileAdded(tile, event):
    """Inform the ITileBookkeeping adapter for the tile's new parent that
    it has just been added.
    """
    
    context = getMultiAdapter((event.newParent, tile.request, tile), ITileDataContext)
    bookkeeping = ITileBookkeeping(context, None)
    if bookkeeping is not None:
        bookkeeping.added(tile.__name__, tile.id)

@adapter(ITile, IObjectRemovedEvent)
def recordTileRemoved(tile, event):
    """Inform the ITileBookkeeping adapter for the tile's old parent that
    it has just been removed.
    """
    
    context = getMultiAdapter((event.oldParent, tile.request, tile), ITileDataContext)
    bookkeeping = ITileBookkeeping(context, None)
    if bookkeeping is not None:
        bookkeeping.removed(tile.id)

class AnnotationsTileBookkeeping(object):
    """Default adapter for tile bookkeeping.
    
    This stores a btree in annotations on the content object, with tile ids
    as keys and tile types as values.
    """
    
    implements(ITileBookkeeping)
    adapts(IAnnotatable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
    
    def added(self, tileType, tileId):
        
        # Copy, get and re-set the data rather than update it, so that we will
        # write to the draft storage when appropriate
        
        tree = dict(self.annotations.get(ANNOTATIONS_KEY, {}))
        tree[tileId] = tileType
        self.annotations[ANNOTATIONS_KEY] = tree
        
        counter = self.counter()
        self.annotations[COUNTER_KEY] = counter + 1
    
    def removed(self, tileId):
        
        # Copy, get and re-set the data rather than update it, so that we will
        # write to the draft storage when appropriate
        
        tree = dict(self.annotations.get(ANNOTATIONS_KEY, {}))
        if tileId in tree:
            del tree[tileId]
            self.annotations[ANNOTATIONS_KEY] = tree
            return True
        
        return False
    
    def counter(self):
        return self.annotations.get(COUNTER_KEY, 0)
    
    def typeOf(self, tileId):
        tree = self.annotations.get(ANNOTATIONS_KEY, {})
        return tree.get(tileId, None)
    
    def enumerate(self, tileType=None):
        tree = self.annotations.get(ANNOTATIONS_KEY, {})
        for tileId, tileTypeStored in tree.iteritems():
            if tileType is None or tileTypeStored == tileType:
                yield (tileId, tileTypeStored,)
