from Acquisition import aq_inner

from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form import form, button
from plone.z3cform import layout

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles.browser.base import TileForm
from plone.app.tiles import MessageFactory as _

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DefaultEditForm(TileForm, form.Form):
    """Standard tile edit form, which is wrapped by DefaultEditView (see below).
    
    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """
    
    tileType = None
    tileURL = None
    
    ignoreContext = False
    
    def __init__(self, context, request):
        super(DefaultEditForm, self).__init__(context, request)
        self.request['disable_border'] = True
    
    def getContent(self):
        typeName = self.tileType.__name__
        
        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse('@@' + typeName)
        
        dataManager = ITileDataManager(tile)
        return dataManager.get()
    
    # UI
    
    @property
    def label(self):
        return _(u"Edit ${name}", mapping={'name': self.tileType.title})
    
    def nextURL(self):
        if self.tileURL is not None:
            return self.tileURL
        
        container = aq_inner(self.context)
        return container.absolute_url()
    
    # Buttons/actions
    
    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
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
        
        notify(ObjectModifiedEvent(tile))
        
        # Get the tile URL, possibly with encoded data
        self.tileURL = absoluteURL(tile, tile.request)
        
        IStatusMessage(self.request).addStatusMessage(_(u"Tile saved to ${url}",
                                                        mapping={'url': self.tileURL}),
                                                      type=u'info')
        
        url = "%s/++edittile++%s?id=%s" % (self.context.absolute_url(), typeName,
                                           tile.id)
        self.request.response.redirect(url)

        
    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL()) 

    def updateActions(self):
        super(DefaultEditForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")
    
class DefaultEditView(layout.FormWrapper):
    """This is the default edit view as looked up by the ++edittile++ traversal
    namespace adapter from plone.tiles. It is an unnamed adapter on 
    (context, request, tileType).
    
    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """
    
    form = DefaultEditForm
    index = ViewPageTemplateFile('addedit.pt')

    
    def __init__(self, context, request, tileType):
        super(DefaultEditView, self).__init__(context, request)
        self.tileType = tileType

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and getattr(self.form_instance, 'tileType', None) is None: 
            self.form_instance.tileType = tileType
