# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
import pkg_resources
import re

try:
    pkg_resources.get_distribution('plone.app.drafts')
except pkg_resources.DistributionNotFound:
    HAS_DRAFTS = False
else:
    HAS_DRAFTS = True

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestTileLifecycle(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        app = self.layer['app']
        self.browser = Browser(app)
        self.browser.handleErrors = False

    def test_transient_lifecycle(self):
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD, )
        )

        # Add a new transient tile using the @@add-tile view
        self.browser.open('{0}/@@add-tile'.format(self.portal_url))
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.transient']
        self.browser.getControl(name='form.button.Create').click()

        # Now we are at the transient tile add form
        url = '{0}/@@add-tile/plone.app.tiles.demo.transient'
        self.assertEqual(
            self.browser.url,
            url.format(self.portal_url),
        )

        # Fill the form
        name = 'plone.app.tiles.demo.transient.message'
        self.browser.getControl(name=name).value = 'Test message'
        self.browser.getControl(label='Save').click()

        # See the tile
        self.assertTrue('<b>Transient tile Test message</b>' in
                        self.browser.contents)

        # Edit the tile
        # prepend @@edit-tile to the tile type
        url = self.browser.url.replace('@@', '@@edit-tile/')
        self.browser.open(url)
        name = 'plone.app.tiles.demo.transient.message'
        self.browser.getControl(name=name).value = 'New message'
        self.browser.getControl(label='Save').click()
        self.assertTrue('<b>Transient tile New message</b>' in
                        self.browser.contents)

        # get the tile id
        tile_id_regex = re.search('(?P<id>[\w-]+)\?', self.browser.url)
        self.assertTrue(tile_id_regex)  # will fail if is None
        tile_id = tile_id_regex.group('id')

        # a transient tile can not be removed,
        # so trying to access the @@delete-tile will raise NotFound
        delete_url = '{0}/@@delete-tile/{1}'.format(self.portal_url,
                                                    tile_id)
        self.assertRaises(NotFound, self.browser.open, delete_url)

    def test_persistent_lifecycle(self):
        folder_annotations = IAnnotations(self.portal)
        tile_id = 'tile-1'
        annotations_key = '{0}.{1}'.format(ANNOTATIONS_KEY_PREFIX, tile_id)

        self.assertEqual(None, folder_annotations.get(annotations_key))

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

        # Fill in the data and save
        name = 'plone.app.tiles.demo.persistent.message'
        message = 'Test message'
        self.browser.getControl(name=name).value = message
        counter = 1
        name = 'plone.app.tiles.demo.persistent.counter'
        self.browser.getControl(name=name).value = str(counter)
        self.browser.getControl(label='Save').click()

        # View the tile
        msg = '<b>Persistent tile {0} #{1}</b>'.format(message, counter)
        self.assertTrue(msg in self.browser.contents)

        # Verify annotations
        self.assertEqual(message,
                         folder_annotations[annotations_key]['message'])
        self.assertEqual(counter,
                         folder_annotations[annotations_key]['counter'])

        # Edit the tile
        # prepend @@edit-tile to the tile type
        url = self.browser.url.replace('@@', '@@edit-tile/')
        self.browser.open(url)
        name = 'plone.app.tiles.demo.persistent.message'
        new_message = 'New message'
        self.browser.getControl(name=name).value = new_message
        self.browser.getControl(label='Save').click()

        # View the tile
        msg = '<b>Persistent tile {0} #{1}</b>'.format(new_message, counter)
        self.assertTrue(msg in self.browser.contents)

        # Verify annotations
        self.assertEqual(new_message,
                         folder_annotations[annotations_key]['message'])
        self.assertEqual(counter,
                         folder_annotations[annotations_key]['counter'])

        # Remove the tile
        self.browser.open('{0}/@@delete-tile/{1}/{2}'.format(
            self.portal_url, "plone.app.tiles.demo.persistent", tile_id))
        self.browser.getControl(label='Delete').click()

        # Verify status code
        self.assertEqual('200 Ok', self.browser.headers['status'])

        # Verify annotations
        self.assertEqual(None, folder_annotations.get(annotations_key))
