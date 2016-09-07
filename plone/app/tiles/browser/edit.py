# -*- coding: utf-8 -*-
from Acquisition import Implicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.tiles import _ as _
from plone.app.tiles.browser.base import TileForm
from plone.app.tiles.utils import appendJSONData
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform import layout
from plone.z3cform.interfaces import IDeferSecurityCheck
from z3c.form import form, button
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.traversing.browser.absoluteurl import absoluteURL
import logging

logger = logging.getLogger('plone.app.tiles')


class AcquirableDictionary(dict, Implicit):
    """Wrapper to make tile data dictionary acquirable and permission aware"""


class DefaultEditForm(TileForm, form.Form):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    name = "edit_tile"

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
        # query string parameters from the original request It is necessary to
        # defer security checking because during initial form setup, the
        # security context is not yet set. Setting the IDeferSecurityCheck
        # interface on the request is handled in
        # plone.z3cform.traversal.FormWidgetTraversal
        if IDeferSecurityCheck.providedBy(self.request):
            tile = self.context.unrestrictedTraverse(
                '@@%s/%s' % (typeName, tileId,))
        else:
            tile = self.context.restrictedTraverse(
                '@@%s/%s' % (typeName, tileId,))

        dataManager = ITileDataManager(tile)
        return AcquirableDictionary(dataManager.get()).__of__(self.context)

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
        tile = self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, self.tileId,))

        dataManager = ITileDataManager(tile)
        new_data = {}
        form.applyChanges(self, new_data, data)
        dataManager.set(new_data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)

        notify(ObjectModifiedEvent(tile))
        logger.debug(u"Tile edited at {0}".format(tileURL))

        try:
            url = self.nextURL(tile)
        except NotImplementedError:
            url = tileURL

        self.request.response.redirect(url)

    def nextURL(self, tile):
        raise NotImplementedError

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        url = appendJSONData(self.action, '#', {'action': "cancel"})
        url = url.replace('@@' + self.name.replace('_', '-') + '/', '@@')
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

    @property
    def tileId(self):
        return getattr(self.form_instance, 'tileId', None)

    @tileId.setter
    def tileId(self, value):
        self.form_instance.tileId = value

    def __init__(self, context, request, tileType):
        super(DefaultEditView, self).__init__(context, request)
        self.tileType = tileType

        # Configure the form instance
        if self.form_instance is not None:
            if getattr(self.form_instance, 'tileType', None) is None:
                self.form_instance.tileType = tileType
