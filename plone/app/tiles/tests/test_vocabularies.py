# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.app.tiles.interfaces import ALLOWED_TILES_VOCABULARY
from plone.app.tiles.interfaces import AVAILABLE_TILES_VOCABULARY
from plone.app.tiles.interfaces import REGISTERED_TILES_VOCABULARY
from plone.app.tiles.testing import PLONE_APP_TILES_INTEGRATION_TESTING

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestVocabularies(unittest.TestCase):

    layer = PLONE_APP_TILES_INTEGRATION_TESTING

    def testRegisteredTilesVocabulary(self):
        factory = getUtility(IVocabularyFactory,
                             name=REGISTERED_TILES_VOCABULARY)
        vocabulary = factory(self.layer['portal'])
        self.assertEqual(len(vocabulary), 2)

    def testAvailableTilesVocabulary(self):
        factory = getUtility(IVocabularyFactory,
                             name=AVAILABLE_TILES_VOCABULARY)
        vocabulary = factory(self.layer['portal'])
        self.assertEqual(len(vocabulary), 2)

    def testAllowedTilesVocabulary(self):
        logout()
        factory = getUtility(IVocabularyFactory,
                             name=ALLOWED_TILES_VOCABULARY)
        vocabulary = factory(self.layer['portal'])
        self.assertEqual(len(vocabulary), 0)

        setRoles(self.layer['portal'], TEST_USER_ID, ['Editor'])
        login(self.layer['portal'], TEST_USER_NAME)
        vocabulary = factory(self.layer['portal'])
        self.assertEqual(len(vocabulary), 2)
