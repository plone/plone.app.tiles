"""Event handlers to keep a list of tiles
"""

from BTrees.OOBTree import OOBTree

from zope.component import adapts
from zope.interface import implements
from zope.component import adapter

from zope.annotation.interfaces import IAnnotatable, IAnnotations

from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from plone.tiles.interfaces import ITile

from plone.app.tiles.interfaces import ITileBookkeeping

ANNOTATIONS_KEY = "plone.app.tiles.bookkeeping"
COUNTER_KEY = "plone.app.tiles.counter"

@adapter(ITile, IObjectAddedEvent)
def recordTileAdded(tile, event):
    """Inform the ITileBookkeeping adapter for the tile's new parent that
    it has just been added.
    """
    
    bookkeeping = ITileBookkeeping(event.newParent, None)
    if bookkeeping is not None:
        bookkeeping.added(tile.__name__, tile.id)

@adapter(ITile, IObjectRemovedEvent)
def recordTileRemoved(tile, event):
    """Inform the ITileBookkeeping adapter for the tile's old parent that
    it has just been removed.
    """

    bookkeeping = ITileBookkeeping(event.oldParent, None)
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
        tree = self.annotations.setdefault(ANNOTATIONS_KEY, OOBTree())
        tree[tileId] = tileType
        
        counter = self.annotations.setdefault(COUNTER_KEY, 0)
        self.annotations[counter] += 1
    
    def removed(self, tileId):
        tree = self.annotations.get(ANNOTATIONS_KEY, {})
        if tileId in tree:
            del tree[tileId]
            return True
        return False
    
    def counter(self):
        return self.annotations.get(COUNTER_KEY, 0)
    
    def typeOf(self, tileId):
        tree = self.annotations.get(ANNOTATIONS_KEY, {})
        return tree.get(tileId, None)
    
    def enumerate(self, tileType=None):
        tree = self.annotations.setdefault(ANNOTATIONS_KEY, {})
        for tileId, tileTypeStored in tree.iteritems():
            if tileType is None or tileTypeStored == tileType:
                yield (tileId, tileTypeStored,)
