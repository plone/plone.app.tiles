# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.dexterity.fti import DexterityFTI
from zope.component import getUtility
from zope.component import provideUtility
import plone.app.dexterity
import plone.app.relationfield
import plone.app.tiles

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.drafts')
except pkg_resources.DistributionNotFound:
    HAS_DRAFTS = False
else:
    import plone.app.drafts
    HAS_DRAFTS = True


class PloneAppTiles(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=plone.app.relationfield)
        if HAS_DRAFTS:
            self.loadZCML(package=plone.app.drafts)
        self.loadZCML(package=plone.app.tiles)
        self.loadZCML(package=plone.app.tiles, name='demo.zcml')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.relationfield:default')
        if HAS_DRAFTS:
            applyProfile(portal, 'plone.app.drafts:default')
        applyProfile(portal, 'plone.app.tiles:default')
        self.registerFTI(portal)

    def registerFTI(self, portal):
        types_tool = getToolByName(portal, 'portal_types')
        fti = DexterityFTI(
            'Page',
            global_allow=True,
            behaviors=(
                'plone.app.dexterity.behaviors.metadata.IBasic',
                'plone.app.drafts.interfaces.IDraftable',
            )
        )
        types_tool._setObject('Page', fti)

    # Temporarily set up a more predictable UUID generator so that we can
    # rely on the uuids in tests

    def testSetUp(self):
        from plone.uuid.interfaces import IUUIDGenerator

        class FauxUUIDGenerator(object):

            counter = 0

            def __call__(self):
                self.counter += 1
                return 'tile-%d' % self.counter

        self._uuidGenerator = getUtility(IUUIDGenerator)
        provideUtility(FauxUUIDGenerator(), provides=IUUIDGenerator)

    def testTearDown(self):
        from plone.uuid.interfaces import IUUIDGenerator
        provideUtility(self._uuidGenerator, provides=IUUIDGenerator)

PLONE_APP_TILES_FIXTURE = PloneAppTiles()
PLONE_APP_TILES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_TILES_FIXTURE,),
    name="PloneAppTilesLayer:Integration")
PLONE_APP_TILES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_TILES_FIXTURE,),
    name="PloneAppTilesLayer:Functional")
