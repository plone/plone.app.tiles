# -*- coding: utf-8 -*-
from plone.app.tiles.demo import TransientTile
from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestTileTraversal(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_restrictedTraverse(self):
        # The easiest way to look up a tile in Zope 2 is to use traversal:

        traversed = self.portal.restrictedTraverse(
            '@@plone.app.tiles.demo.transient/tile-1')
        self.assertTrue(isinstance(traversed, TransientTile))
        self.assertEqual('plone.app.tiles.demo.transient', traversed.__name__)
        self.assertEqual('tile-1', traversed.id)
