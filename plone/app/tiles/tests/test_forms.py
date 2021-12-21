# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.tiles.browser.base import TileForm
from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
from plone.tiles.interfaces import ITileType
from z3c.form.datamanager import DictionaryField
from z3c.form.interfaces import NOT_CHANGED
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.component import queryUtility


try:
    import unittest2 as unittest
except ImportError:
    import unittest


class WrappedEditForm(DefaultEditForm):
    _dummy_data = {}

    def update(self):
        # DefaultEditForm.update() fails in checkPermission because of a missing interaction.
        # We can skip the funkyness.
        super(TileForm, self).update()

    def set_dummy_data(self, data):
        self._dummy_data = data

    def extractData(self):
        """Extract data from request.

        Here we override to make it easy to mock different data.
        We return data and errors
        """
        return self._dummy_data, {}


class TestTileDrafting(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        app = self.layer["app"]
        self.browser = Browser(app)
        self.browser.handleErrors = False

        # Log in
        self.browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

        # Add a new persistent tile using the @@add-tile view
        self.browser.open("{0}/@@add-tile".format(self.portal_url))
        self.browser.getControl(name="tiletype").value = [
            "plone.app.tiles.demo.persistent"
        ]
        self.browser.getControl(name="form.button.Create").click()

    def test_data_manager_add_form(self):
        """Test that appropriate IDataManagers are used when processing tile
        add and edit forms."""

        # This data manager counts how many times set() is called so we
        # can make sure it's getting used
        class SetCountingDataManager(DictionaryField):
            set_called = 0

            def set(self, value):
                SetCountingDataManager.set_called += 1
                DictionaryField.set(self, value)

        provideAdapter(SetCountingDataManager)

        try:
            # Fill in the data and save
            name = "plone.app.tiles.demo.persistent.message"
            message = "Test message"
            self.browser.getControl(name=name).value = message
            counter = 1
            name = "plone.app.tiles.demo.persistent.counter"
            self.browser.getControl(name=name).value = str(counter)
            self.browser.getControl(label="Save").click()

            # Set should have been called three times, once for each field
            self.assertEqual(SetCountingDataManager.set_called, 3)

            SetCountingDataManager.set_called = 0
            url = self.browser.url.replace("@@", "@@edit-tile/")
            self.browser.open(url)
            name = "plone.app.tiles.demo.persistent.message"
            self.browser.getControl(name=name).value = "blah"
            self.browser.getControl(label="Save").click()

            # Should have been called twice now,
            # because the counter field has not changed.
            self.assertEqual(SetCountingDataManager.set_called, 2)
        finally:
            # Make sure our useless data manager gets deregistered so it
            # doesn't break everything
            gsm = getGlobalSiteManager()
            gsm.unregisterAdapter(factory=SetCountingDataManager)

    def test_edit_form_save_data(self):
        """Test that the edit form saves and keeps data correctly.

        We use a wrapper around the edit form for this, to avoid some setup troubles.
        """
        # http://nohost/plone/@@edit-tile/plone.app.tiles.demo.persistent/tile-1

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        form = WrappedEditForm(self.portal, self.portal.REQUEST)
        tileType = "plone.app.tiles.demo.persistent"
        form.tileType = queryUtility(ITileType, name=tileType)
        form.tileId = "tile-1"
        form.update()
        # Check the default.
        content = form.getContent()
        # Comparing two dicts is apparently not done in Python 3.  So we split.
        self.assertListEqual(
            sorted(list(content.keys())),
            sorted(["message", "counter", "image"]),
        )
        self.assertIsNone(content["message"])
        self.assertIsNone(content["counter"])

        # Handle a save.  To fake a POST request, we use dummy data.
        form.set_dummy_data({"message": "hello", "counter": 1})
        # We need to pass a form and an action.
        # action is ignored by our handleSave method.
        form.handleSave(form=form, action=None)
        content = form.getContent()
        # Comparing two dicts is apparently not done in Python 3.  So we split.
        self.assertListEqual(
            sorted(list(content.keys())),
            sorted(["message", "counter", "image"]),
        )
        self.assertEqual(content["message"], "hello")
        self.assertEqual(content["counter"], 1)

        # If a field is there, but its value is the marker NOT_CHANGED,
        # then we keep the previous value.
        # This is what happens when you have previously uploaded an image,
        # and when editing you want to keep the current image.
        # See https://github.com/plone/plone.app.tiles/issues/36
        form.set_dummy_data({"message": NOT_CHANGED, "counter": 2})
        form.handleSave(form=form, action=None)
        content = form.getContent()
        self.assertListEqual(
            sorted(list(content.keys())),
            sorted(["message", "counter", "image"]),
        )
        self.assertEqual(content["message"], "hello")
        self.assertEqual(content["counter"], 2)

        # Only pass one of the fields.
        # The other field should remain in the data.
        form.set_dummy_data({"message": "bye"})
        form.handleSave(form=form, action=None)
        content = form.getContent()
        self.assertListEqual(
            sorted(list(content.keys())),
            sorted(["message", "counter", "image"]),
        )
        self.assertEqual(content["message"], "bye")
        self.assertEqual(content["counter"], 2)
