from zope.component import getUtility
from zope.component import provideUtility

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class PloneAppTiles(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.tiles
        xmlconfig.file('configure.zcml', plone.app.tiles, context=configurationContext)
        xmlconfig.file('demo.zcml', plone.app.tiles, context=configurationContext)
        
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.tiles:default')
    
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
PLONE_APP_TILES_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONE_APP_TILES_FIXTURE,), name="plone.app.tiles:Integration")
PLONE_APP_TILES_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(PLONE_APP_TILES_FIXTURE,), name="plone.app.tiles:Functional")
