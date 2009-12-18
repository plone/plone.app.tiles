import urllib

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
        tileURL = absoluteURL(tile, tile.request)
        
        IStatusMessage(self.request).addStatusMessage(
                _(u"Tile created at ${url}", mapping={'url': tileURL}), type=u'info'
            )
        
        # Inject @@edit-tile into the URL
        urlParts = tileURL.split('/')
        urlParts.insert(-1, '@@edit-tile')
        if urlParts[-1].startswith('@@'):
            urlParts[-1] = urlParts[-1][2:]
        
        # Add JSON data string
        tileDataJson = {}
        tileDataJson['action'] = "save"
        tileDataJson['url'] = tileURL
        tileDataJson['type'] = typeName
        tileDataJson['id'] = tile.id
        
        url = '/'.join(urlParts) + "&tiledata=%s" % (urllib.quote(json.dumps(tileDataJson)),)
        self.request.response.redirect(url)
        
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        tileDataJson = {}
        tileDataJson['action'] = "cancel"
        url = self.request.getURL()
        url += "?tiledata=%s" % (urllib.quote(json.dumps(tileDataJson)))
        self.request.response.redirect(url)

    def updateActions(self):
        super(DefaultAddForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")
    
class DefaultAddView(layout.FormWrapper):
    """This is the default add view as looked up by the @@add-tile traversal
    view. It is an unnamed adapter on  (context, request, tileType).
    
    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """
    
    form = DefaultAddForm
    index = ViewPageTemplateFile('tileformlayout.pt')
    
    def __init__(self, context, request, tileType):
        super(DefaultAddView, self).__init__(context, request)
        self.tileType = tileType

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and getattr(self.form_instance,
                                                      'tileType', None) is None: 
            self.form_instance.tileType = tileType
