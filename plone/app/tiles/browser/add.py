from Acquisition import aq_inner

from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form import form, button
from plone.z3cform import layout

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles.browser.base import TileForm
from plone.app.tiles import MessageFactory as _

from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify

from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    import json
except:
    import simplejson as json

class DefaultAddForm(TileForm, form.Form):
    """Standard tile add form, which is wrapped by DefaultAddView (see below).
    
    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """
    
    tileType = None
    tileURL = None
    
    ignoreContext = True
    
    def __init__(self, context, request):
        super(DefaultAddForm, self).__init__(context, request)
        self.request['disable_border'] = True
    
    # UI
    
    @property
    def label(self):
        return _(u"Add ${name}", mapping={'name': self.tileType.title})
    
    def nextURL(self):
        if self.tileURL is not None:
            return self.tileURL
        
        container = aq_inner(self.context)
        return container.absolute_url()
    
    # Buttons/actions
    
    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        typeName = self.tileType.__name__
        tileId = data.pop('id', None)
        
        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse('@@' + typeName)
        tile.id = tileId
        
        dataManager = ITileDataManager(tile)
        dataManager.set(data)
        
        notify(ObjectCreatedEvent(tile))
        
        # Get the tile URL, possibly with encoded data
        self.tileURL = absoluteURL(tile, tile.request)
        
        #IStatusMessage(self.request).addStatusMessage(
            #_(u"Tile saved to ${url}", mapping={'url': self.tileURL}),
            #type=u'info')
        IStatusMessage(self.request).addStatusMessage(_(u"Tile Saved"))
        
        tileInfoJson = {}
        tileInfoJson['tileURL'] = self.tileURL
        tileInfoJson['type'] = typeName
        tileInfoJson['id'] = tile.id
        
        url = "%s/++edittile++%s?id=%s&tiledata=%s" % (self.context.absolute_url(),
                                           typeName,
                                           tile.id,
                                           json.dumps(tileInfoJson))
        
        # Adding the form input to the url 
        #for item in tile.request.form.keys():
            #url += "&%s=%s" % (item, tile.request.form.get(item))
        
        self.request.response.redirect(url)
        
        
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL()) 

    def updateActions(self):
        super(DefaultAddForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")
    
class DefaultAddView(layout.FormWrapper):
    """This is the default add view as looked up by the ++addtile++ traversal
    namespace adapter from plone.tiles. It is an unnamed adapter on 
    (context, request, tileType).
    
    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """
    
    form = DefaultAddForm
    index = ViewPageTemplateFile('addedit.pt')
    
    def __init__(self, context, request, tileType):
        super(DefaultAddView, self).__init__(context, request)
        self.tileType = tileType

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and getattr(self.form_instance, 'tileType', None) is None: 
            self.form_instance.tileType = tileType
