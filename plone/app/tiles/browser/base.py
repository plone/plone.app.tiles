from zope.component import getMultiAdapter
from zope.security import checkPermission

from AccessControl import Unauthorized

from z3c.form.interfaces import IWidgets
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.interfaces import IDeferSecurityCheck

from plone.app.drafts.interfaces import ICurrentDraftManagement


class TileFormLayout(object):
    """Layout view giving access to macro slots
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def macros(self):
        return self.index.macros


class TileForm(AutoExtensibleForm):
    """Mixin class for tile add/edit forms, which will load the tile schema
    and set up an appropriate form.
    """

    # Must be set by subclass
    tileType = None
    tileId = None

    # Get fieldets if subclass sets additional_schemata
    autoGroups = True

    # We don't want the tile edit screens to use a form prefix, so that we
    # can pass simple things on the edit screen and have them be interpreted
    # by transient tiles
    prefix = ''

    def update(self):

        # Set up draft information if required
        currentDraft = ICurrentDraftManagement(self.request)
        currentDraft.mark()

        # Override to check the tile add/edit permission
        if not IDeferSecurityCheck.providedBy(self.request):
            if not checkPermission(self.tileType.add_permission, self.context):
                raise Unauthorized(
                    "You are not allowed to add this kind of tile")

        super(TileForm, self).update()

    def render(self):
        if self.request.response.getStatus() in (301, 302):
            return ''
        return super(TileForm, self).render()

    def updateWidgets(self):
        # Override to set the widgets prefix before widgets are updated
        self.widgets = getMultiAdapter((self, self.request, self.getContent()),
            IWidgets)
        self.widgets.prefix = ''
        self.widgets.mode = self.mode
        self.widgets.ignoreContext = self.ignoreContext
        self.widgets.ignoreRequest = self.ignoreRequest
        self.widgets.ignoreReadonly = self.ignoreReadonly
        self.widgets.update()

    @property
    def description(self):
        return self.tileType.description

    # AutoExtensibleForm contract

    @property
    def schema(self):
        return self.tileType.schema

    additionalSchemata = ()
