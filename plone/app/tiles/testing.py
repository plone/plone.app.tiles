# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.component import getUtility
from zope.component import provideUtility
from zope.configuration import xmlconfig

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.drafts')
except pkg_resources.DistributionNotFound:
    HAS_DRAFTS = False
else:
    HAS_DRAFTS = True


class PloneAppTiles(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        if HAS_DRAFTS:
            import plone.app.drafts
            xmlconfig.file(
                'configure.zcml',
                plone.app.drafts,
                context=configurationContext)
        import plone.app.tiles
        xmlconfig.file(
            'configure.zcml',
            plone.app.tiles,
            context=configurationContext)
        xmlconfig.file(
            'demo.zcml',
            plone.app.tiles,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        if HAS_DRAFTS:
            applyProfile(portal, 'plone.app.drafts:default')
        applyProfile(portal, 'plone.app.tiles:default')

        from plone.registry.interfaces import IRegistry

        registry = getUtility(IRegistry)
        registry['plone.app.tiles'] = [
            u'plone.app.tiles.demo.transient',
            u'plone.app.tiles.demo.persistent',
        ]

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
