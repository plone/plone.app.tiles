# -*- coding: utf-8 -*-
from plone.app.tiles.browser.base import TileForm
from plone.app.tiles import _
from plone.app.tiles.utils import appendJSONData
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform import layout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.traversing.browser import absoluteURL
import logging

logger = logging.getLogger('plone.app.tiles')


class DefaultDeleteForm(TileForm, form.Form):
    """Standard tile delete form, which is wrapped by DefaultDeleteView (see
    below).
    """

    name = "delete_tile"

    # Set during traversal
    tileType = None
    tileId = None

    ignoreContext = True

    schema = None

    def __init__(self, context, request):
        super(DefaultDeleteForm, self).__init__(context, request)
        self.request['disable_border'] = True

    # UI

    @property
    def label(self):
        return _(u"Delete ${name}", mapping={'name': self.tileType.title})

    # Buttons/actions

    @button.buttonAndHandler(_('Delete'), name='delete')
    def handleDelete(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        typeName = self.tileType.__name__

        # Traverse to the tile about to be removed
        tile = self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, self.tileId,))
        # Look up the URL - we need to do this before we've deleted the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)

        dataManager = ITileDataManager(tile)
        dataManager.delete()

        notify(ObjectRemovedEvent(tile, self.context, self.tileId))
        logger.debug(u"Tile deleted at {0}".format(tileURL))

        # Skip form rendering for AJAX requests
        if self.request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            IStatusMessage(self.request).addStatusMessage(
                _(u"Tile deleted at ${url}", mapping={'url': tileURL}),
                type=u'info'
            )
            self.template = lambda: u''
            return

        try:
            url = self.nextURL(tile)
        except NotImplementedError:
            url = self.context.absolute_url()

        self.request.response.redirect(url)

    def nextURL(self, tile):
        raise NotImplementedError

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        url = appendJSONData(self.action, '#', {'action': "cancel"})
        url = url.replace('@@' + self.name.replace('_', '-') + '/', '@@')
        self.request.response.redirect(url)

    def updateActions(self):
        super(DefaultDeleteForm, self).updateActions()
        self.actions["delete"].addClass("context")
        self.actions["cancel"].addClass("standalone")


class DefaultDeleteView(layout.FormWrapper):
    """This is the default delete view as looked up by the @@delete-tile
    traveral view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = DefaultDeleteForm
    index = ViewPageTemplateFile('tileformlayout.pt')

    # Set by sub-path traversal in @@delete-tile - we delegate to the form

    @property
    def tileId(self):
        return getattr(self.form_instance, 'tileId', None)

    @tileId.setter
    def tileId(self, value):
        self.form_instance.tileId = value

    def __init__(self, context, request, tileType):
        super(DefaultDeleteView, self).__init__(context, request)
        self.tileType = tileType

        # Configure the form instance
        if self.form_instance is not None:
            if getattr(self.form_instance, 'tileType', None) is None:
                self.form_instance.tileType = tileType
