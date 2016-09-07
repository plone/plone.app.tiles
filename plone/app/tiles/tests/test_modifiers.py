# -*- coding: utf-8 -*-
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.tiles.modifiers import CleanTileAnnotations
from plone.app.tiles.testing import PLONE_APP_TILES_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.namedfile import NamedBlobFile
from plone.tiles import PersistentTile
from plone.tiles.interfaces import ITileDataManager
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import pickle
import StringIO
import unittest


class Tile(PersistentTile):
    pass


class TestModifiers(unittest.TestCase):

    layer = PLONE_APP_TILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # we need to have the Manager role to be able to add things
        # to the portal root
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

    def testCleanTileDataModifier(self):
        # Create page and tile
        page = createContentInContainer(self.portal, 'Page')
        related = createContentInContainer(self.portal, 'Page')
        tile = Tile(page, self.request)
        tile.id = 'mytile'

        # Set tile data
        data = {
            'boolean': True,
            'blob': NamedBlobFile('dummy test data', filename=u'test.txt'),
            'iterable': PersistentList([
                NamedBlobFile('dummy test data', filename=u'test.txt'),
                NamedBlobFile('dummy test data', filename=u'test.txt'),
            ]),
            'mapping': PersistentMapping({
                'blob': NamedBlobFile('dummy test data', filename=u'test.txt'),
            }),
            'relation': RelationValue(getUtility(IIntIds).getId(page)),
        }
        data['relation'].from_object = related
        dm = ITileDataManager(tile)
        dm.set(data)

        # Call modifier
        modifier = CleanTileAnnotations()
        callbacks = modifier.getOnCloneModifiers(page)

        # The modifier works by preventing CMFEditions deepcopy to clone blobs
        # and relations in tile annotations. We simulate this in test by
        # creating a custom pickler and configuring it with modifier callbacks.
        src = StringIO.StringIO()
        pickler = pickle.Pickler(src)
        pickler.persistent_id = callbacks[0]
        unpickler = pickle.Unpickler(src)
        unpickler.persistent_load = callbacks[1]

        # Deepcopy object with our modifier configured picklers
        pickler.dump(page.aq_base)  # pickle unwrapped object
        src.seek(0)
        clone = unpickler.load()

        # Get tile data from the clone
        clone_tile = Tile(clone, self.request)
        clone_tile.id = 'mytile'
        clone_dm = ITileDataManager(clone_tile)
        clone_data = clone_dm.get()

        # Test that blobs and relations has been cloned with None
        self.assertIn('boolean', clone_data)
        self.assertIn('blob', clone_data)
        self.assertIn('iterable', clone_data)
        self.assertIn('mapping', clone_data)
        self.assertIn('relation', clone_data)
        self.assertEqual(clone_data['boolean'], True)
        self.assertEqual(clone_data['blob'], None)
        self.assertEqual(clone_data['iterable'], [None, None])
        self.assertEqual(clone_data['mapping'], {'blob': None})
        self.assertEqual(clone_data['relation'], None)

        # Test that retriever will set values from working copy
        modifier.afterRetrieveModifier(page, clone)

        # Test that data equals after retrieve
        clone_data = clone_dm.get()
        self.assertEqual(clone_data['boolean'], data['boolean'])
        self.assertEqual(clone_data['blob'], data['blob'])
        self.assertEqual(clone_data['iterable'], data['iterable'])
        self.assertEqual(clone_data['mapping'], data['mapping'])
        self.assertEqual(clone_data['relation'], data['relation'])
