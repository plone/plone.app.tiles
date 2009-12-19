import unittest
from zope.testing import doctest

from Products.PloneTestCase import ptc
from Products.Five import zcml
from Products.Five.testbrowser import Browser

import collective.testcaselayer.ptc

import plone.app.tiles

from zope.annotation.interfaces import IAnnotations

from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from plone.app.tiles.demo import TransientTile

ptc.setupPloneSite()

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        zcml.load_config('configure.zcml', plone.app.tiles)
        zcml.load_config('demo.zcml', plone.app.tiles)

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class FunctionalTest(ptc.FunctionalTestCase):
    
    layer = Layer

    def afterSetUp(self):
        self.browser = Browser()
        self.browser.handleErrors = False
    
    def test_transient_lifecycle(self):
        # Log in
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (ptc.default_user, ptc.default_password,))
        
        # Add a new transient tile using the @@add-tile view
        self.browser.open(self.folder.absolute_url() + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.transient']
        self.browser.getControl(name='id').value = "tile1"
        self.browser.getControl(name='form.button.Create').click()
        
        # Fill in the data and save
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile1?message=Test+message&' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22http%3A//nohost/plone/Members/test_user_1_/%40%40plone.app.tiles.demo.transient/tile1%3Fmessage%3DTest%2Bmessage%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.transient%22%2C%20%22id%22%3A%20%22tile1%22%7D',
                          self.browser.url)

        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.transient/tile1?message=Test+message')
        self.assertEquals("<html><body><b>Transient tile Test message</b></body></html>", self.browser.contents)
        
        # Edit the tile
        self.browser.open(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile1?message=Test+message')
        self.browser.getControl(name='message').value = 'New message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile1?message=New+message&' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22http%3A//nohost/plone/Members/test_user_1_/%40%40plone.app.tiles.demo.transient/tile1%3Fmessage%3DNew%2Bmessage%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.transient%22%2C%20%22id%22%3A%20%22tile1%22%7D',
                          self.browser.url)

        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.transient/tile1?message=New+message')
        self.assertEquals("<html><body><b>Transient tile New message</b></body></html>", self.browser.contents)
        
        # Remove the tile (really a no-op for transient tiles)
        self.browser.open(self.folder.absolute_url() + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.transient']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.transient', self.browser.getControl(name='deleted.type').value)
        
        # Return to the content object
        self.browser.getControl(label='OK').click()
        self.assertEquals(self.folder.absolute_url() + '/view', self.browser.url)
        
    def test_persistent_lifecycle(self):
        
        folderAnnotations = IAnnotations(self.folder)
        annotationsKey = "%s.tile2" % ANNOTATIONS_KEY_PREFIX
        
        self.assertEquals(None, folderAnnotations.get(annotationsKey))
        
        # Log in
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (ptc.default_user, ptc.default_password,))
        
        # Add a new persistent tile using the @@add-tile view
        self.browser.open(self.folder.absolute_url() + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='id').value = "tile2"
        self.browser.getControl(name='form.button.Create').click()
        
        # Fill in the data and save
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(name='counter').value = '1'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile2?' + \
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22http%3A//nohost/plone/Members/test_user_1_/%40%40plone.app.tiles.demo.persistent/tile2%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.persistent%22%2C%20%22id%22%3A%20%22tile2%22%7D',
                          self.browser.url)
        
        # Verify annotations
        self.assertEquals('Test message', folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.persistent/tile2')
        self.assertEquals("<html><body><b>Persistent tile Test message #1</b></body></html>", self.browser.contents)
        
        # Edit the tile
        self.browser.open(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile2')
        self.browser.getControl(name='message').value = 'New message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile2?' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22http%3A//nohost/plone/Members/test_user_1_/%40%40plone.app.tiles.demo.persistent/tile2%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.persistent%22%2C%20%22id%22%3A%20%22tile2%22%7D',
                          self.browser.url)
        
        # Verify annotations
        self.assertEquals('New message', folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])

        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.persistent/tile2')
        self.assertEquals("<html><body><b>Persistent tile New message #1</b></body></html>", self.browser.contents)
        
        # Remove the tile
        self.browser.open(self.folder.absolute_url() + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile2'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile2', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent', self.browser.getControl(name='deleted.type').value)
        
        # Verify annotations
        self.assertEquals(None, folderAnnotations.get(annotationsKey))
        
        # Return to the content object
        self.browser.getControl(label='OK').click()
        self.assertEquals(self.folder.absolute_url() + '/view', self.browser.url)
    
    def test_restrictedTraverse(self):
        
        traversed = self.portal.restrictedTraverse('@@plone.app.tiles.demo.transient/tile1')
        self.failUnless(isinstance(traversed, TransientTile))
        self.assertEquals('plone.app.tiles.demo.transient', traversed.__name__)
        self.assertEquals('tile1', traversed.id)
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
