# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.fieldsets.group import Group
from plone.z3cform.interfaces import IDeferSecurityCheck
from z3c.form.interfaces import IWidgets
from zope.component import getMultiAdapter
from zope.security import checkPermission
from zope.traversing.browser.absoluteurl import absoluteURL


try:
    from plone.app.drafts.interfaces import ICurrentDraftManagement

    PLONE_APP_DRAFTS = True
except ImportError:
    PLONE_APP_DRAFTS = False


class TileFormLayout(object):
    """Layout view giving access to macro slots"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def macros(self):
        return self.index.macros


class TileFormGroup(Group):
    """TileForm group class, which prefixes group form fields similarly
    to TileForm"""

    prefix = ""

    def updateWidgets(self, prefix=None):
        # Override to set the widgets prefix before widgets are updated
        # Note: updateWidgets(prefix=...) is not yet supported by
        # z3c.form 2.5.1 used by Plone 4.2
        self.widgets = getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets
        )
        for attrName in (
            "mode",
            "ignoreRequest",
            "ignoreContext",
            "ignoreReadonly",
        ):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        if prefix is not None:
            self.widgets.prefix = prefix
        else:
            self.widgets.prefix = self.parentForm.tileType.__name__
        self.widgets.update()


class TileForm(AutoExtensibleForm):
    """Mixin class for tile add/edit forms, which will load the tile schema
    and set up an appropriate form.
    """

    # Must be set by subclass
    tileType = None
    tileId = None

    # Get fieldets if subclass sets additional_schemata
    autoGroups = True
    group_class = TileFormGroup

    # We set prefix dynamically in updateWidgets
    prefix = ""
    # Note: We used to not want the tile edit screens to use a form prefix, so
    # that we could pass simple things on the edit screen and have them be
    # interpreted by transient tiles, but this was deprecated without no
    # obvious reason in 85bff714b161eca07b66736780f293940f4f1d92

    # Name is used to form the form action url
    name = ""

    @property
    def action(self):
        """See interfaces.IInputForm"""
        if self.tileType and self.tileId and self.name:
            tile = self.context.restrictedTraverse(
                "@@%s/%s"
                % (
                    self.tileType.__name__,
                    self.tileId,
                )
            )
            url = absoluteURL(tile, self.request)
            url = url.replace("@@", "@@" + self.name.replace("_", "-") + "/")
        else:
            url = self.request.getURL()
        return url

    def update(self):
        # Support drafting tile data context
        if PLONE_APP_DRAFTS:
            ICurrentDraftManagement(self.request).mark()

        # Override to check the tile add/edit permission
        if not IDeferSecurityCheck.providedBy(self.request):
            if not checkPermission(self.tileType.add_permission, self.context):
                raise Unauthorized("You are not allowed to add this kind of tile")

        super(TileForm, self).update()

    def render(self):
        if self.request.response.getStatus() in (301, 302):
            return ""
        return super(TileForm, self).render()

    def updateWidgets(self, prefix=None):
        # Override to set the widgets prefix before widgets are updated
        # Note: updateWidgets(prefix=...) is not yet supported by
        # z3c.form 2.5.1 used by Plone 4.2
        self.widgets = getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets
        )
        self.widgets.prefix = prefix or self.tileType.__name__
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
