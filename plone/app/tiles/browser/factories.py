from zope.component import getAllUtilitiesRegisteredFor
from plone.tiles.interfaces import ITileType

from Products.Five.browser import BrowserView

from plone.memoize.view import memoize
from zope.security import checkPermission

from plone.app.tiles import MessageFactory as _

class TileFactories(BrowserView):
    """Get a list of tiles that can be added in the current context
    """
    
    def sortKey(self, type1, type2):
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
        
        types.sort(self.sortKey)
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
                self.request.response.redirect("%s/++addtile++%s?id=%s" % \
                        (self.context.absolute_url(), newTileType, newTileId))
                return ''
            
        return self.index()
