# -*- coding: utf-8 -*-
from plone.app.tiles.browser.base import TileForm
from plone.app.tiles import _
from plone.app.tiles.utils import appendJSONData
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from plone.z3cform import layout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import form, button
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.traversing.browser.absoluteurl import absoluteURL
import logging

logger = logging.getLogger('plone.app.tiles')


class DefaultAddForm(TileForm, form.Form):
    """Standard tile add form, which is wrapped by DefaultAddView (see below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    name = "add_tile"

    # Set during traversal
    tileType = None
    tileId = None

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

        generator = getUtility(IUUIDGenerator)
        tileId = generator()

        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, tileId,))

        dataManager = ITileDataManager(tile)
        new_data = {}
        form.applyChanges(self, new_data, data)
        dataManager.set(new_data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)

        notify(ObjectCreatedEvent(tile))
        notify(ObjectAddedEvent(tile, self.context, tileId))
        logger.debug(u"Tile created at {0}".format(tileURL))

        try:
            url = self.nextURL(tile)
        except NotImplementedError:
            url = tileURL

        self.request.response.redirect(url)

    def nextURL(self, tile):
        raise NotImplementedError

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        url = appendJSONData(self.context.absolute_url(),
                             '#', {'action': "cancel"})
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

    # Set by sub-path traversal in @@add-tile - we delegate to the form

    @property
    def tileId(self):
        return getattr(self.form_instance, 'tileId', None)

    @tileId.setter
    def tileId(self, value):
        self.form_instance.tileId = value

    def __init__(self, context, request, tileType):
        super(DefaultAddView, self).__init__(context, request)
        self.tileType = tileType

        # Configure the form instance
        if self.form_instance is not None:
            if getattr(self.form_instance, 'tileType', None) is None:
                self.form_instance.tileType = tileType
