# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from z3c.form.datamanager import DictionaryField
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter

from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestTileDrafting(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        app = self.layer['app']
        self.browser = Browser(app)
        self.browser.handleErrors = False

    def test_data_manager_add_form(self):
        """Test that appropriate IDataManagers are used when processing tile
        add and edit forms."""

        # Log in
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD, )
        )

        # Add a new persistent tile using the @@add-tile view
        self.browser.open('{0}/@@add-tile'.format(self.portal_url))
        self.browser.getControl(name='tiletype').value = [
            'plone.app.tiles.demo.persistent'
        ]
        self.browser.getControl(name='form.button.Create').click()

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
            name = 'plone.app.tiles.demo.persistent.message'
            message = 'Test message'
            self.browser.getControl(name=name).value = message
            counter = 1
            name = 'plone.app.tiles.demo.persistent.counter'
            self.browser.getControl(name=name).value = str(counter)
            self.browser.getControl(label='Save').click()

            # Set should have been called twice, once for each field
            self.assertEqual(SetCountingDataManager.set_called, 2)

            url = self.browser.url.replace('@@', '@@edit-tile/')
            self.browser.open(url)
            name = 'plone.app.tiles.demo.persistent.message'
            self.browser.getControl(name=name).value = 'blah'
            self.browser.getControl(label='Save').click()

            # Should have been called four times now
            self.assertEqual(SetCountingDataManager.set_called, 4)
        finally:
            # Make sure our useless data manager gets deregistered so it
            # doesn't break everything
            gsm = getGlobalSiteManager()
            gsm.unregisterAdapter(factory=SetCountingDataManager)
