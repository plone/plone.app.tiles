from z3c.form import form, button
from plone.z3cform import layout

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from zope.traversing.browser.absoluteurl import absoluteURL

from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles.browser.base import TileForm
from plone.app.tiles.utils import appendJSONData, getEditTileURL
from plone.app.tiles import MessageFactory as _


class DefaultEditForm(TileForm, form.Form):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    # Set during traversal
    tileType = None
    tileId = None

    ignoreContext = False

    # Avoid the data to be extracted from the request directly by the form
    # instead of using the tile data manager.
    ignoreRequest = True

    def __init__(self, context, request):
        super(DefaultEditForm, self).__init__(context, request)
        self.request['disable_border'] = True

    def update(self):
        if 'buttons.save' in self.request.form or \
           'buttons.cancel' in self.request.form:
            self.ignoreRequest = False

        super(DefaultEditForm, self).update()

    def getContent(self):
        typeName = self.tileType.__name__
        tileId = self.tileId

        # Traverse to the tile. If it is a transient tile, it will pick up
        # query string parameters from the original request
        tile = self.context.restrictedTraverse('@@%s/%s' % (typeName, tileId,))

        dataManager = ITileDataManager(tile)
        return dataManager.get()

    # UI

    @property
    def label(self):
        return _(u"Edit ${name}", mapping={'name': self.tileType.title})

    # Buttons/actions

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        typeName = self.tileType.__name__

        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse('@@%s/%s' % (typeName, self.tileId,))

        dataManager = ITileDataManager(tile)
        dataManager.set(data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)
        contextURL = absoluteURL(tile.context, self.request)
        tileRelativeURL = tileURL

        if tileURL.startswith(contextURL):
            tileRelativeURL = '.' + tileURL[len(contextURL):]

        notify(ObjectModifiedEvent(tile))

        # Get the tile URL, possibly with encoded data
        IStatusMessage(self.request).addStatusMessage(_(u"Tile saved",), type=u'info')

        # Calculate the edit URL and append some data in a JSON structure,
        # to help the UI know what to do.

        url = getEditTileURL(tile, self.request)

        tileDataJson = {}
        tileDataJson['action'] = "save"
        tileDataJson['mode'] = "edit"
        tileDataJson['url'] = tileRelativeURL
        tileDataJson['tile_type'] = typeName
        tileDataJson['id'] = tile.id

        url = appendJSONData(url, 'tiledata', tileDataJson)
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        tileDataJson = {}
        tileDataJson['action'] = "cancel"
        url = self.request.getURL()
        url = appendJSONData(url, 'tiledata', tileDataJson)
        self.request.response.redirect(url)

    def updateActions(self):
        super(DefaultEditForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")


class DefaultEditView(layout.FormWrapper):
    """This is the default edit view as looked up by the @@edit-tile traveral
    view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = DefaultEditForm
    index = ViewPageTemplateFile('tileformlayout.pt')

    # Set by sub-path traversal in @@edit-tile - we delegate to the form

    def __getTileId(self):
        return getattr(self.form_instance, 'tileId', None)

    def __setTileId(self, value):
        self.form_instance.tileId = value
    tileId = property(__getTileId, __setTileId)

    def __init__(self, context, request, tileType):
        super(DefaultEditView, self).__init__(context, request)
        self.tileType = tileType

        # Configure the form instance
        if self.form_instance is not None:
            if getattr(self.form_instance, 'tileType', None) is None:
                self.form_instance.tileType = tileType
