from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility

from zope.lifecycleevent import ObjectRemovedEvent

from AccessControl import Unauthorized

from zope.security import checkPermission
from zope.event import notify

from plone.tiles.interfaces import ITileType
from plone.tiles.interfaces import ITileDataManager

from plone.memoize.view import memoize

from plone.app.drafts.interfaces import ICurrentDraftManagement


class TileDelete(object):
    """Delete a given tile
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

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

        # Set up draft information if required
        currentDraft = ICurrentDraftManagement(self.request)
        currentDraft.mark()

        self.request['disable_border'] = True

        confirm = self.request.form.get('confirm', False)

        self.tileTypeName = self.request.form.get('type', None)
        self.tileId = self.request.form.get('id', None)

        self.deleted = False

        if confirm and self.tileTypeName and self.tileId:

            tileType = getUtility(ITileType, name=self.tileTypeName)

            if not checkPermission(tileType.add_permission, self.context):
                raise Unauthorized("You are not allowed to modify this " + \
                                   "tile type")

            tile = self.context.restrictedTraverse(
                '@@%s/%s' % (self.tileTypeName, self.tileId,))

            dm = ITileDataManager(tile)
            dm.delete()

            notify(ObjectRemovedEvent(tile, self.context, self.tileId))

            self.deleted = True

        elif 'form.button.Ok' in self.request.form:
            self.request.response.redirect(
                self.context.absolute_url() + '/view')
            return ''

        return self.index()
