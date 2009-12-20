import unittest
from zope.testing import doctest

from Products.PloneTestCase import ptc
from Products.Five import zcml
from Products.Five.testbrowser import Browser

import collective.testcaselayer.ptc

import plone.app.tiles

from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent

from zope.annotation.interfaces import IAnnotations

from plone.tiles.interfaces import ITileDataManager
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX

from plone.app.tiles.interfaces import ITileBookkeeping
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

    def test_restrictedTraverse(self):
        
        # The easiest way to look up a tile in Zope 2 is to use traversal:
        
        traversed = self.portal.restrictedTraverse('@@plone.app.tiles.demo.transient/tile1')
        self.failUnless(isinstance(traversed, TransientTile))
        self.assertEquals('plone.app.tiles.demo.transient', traversed.__name__)
        self.assertEquals('tile1', traversed.id)

    def test_forensic_bookkeeping(self):
        
        # The ITileBookkeeping adapter provides a means of listing the tiles
        # in a given context and cleaning up leftover data
        
        # Create a persistent tile with some data
        tile1 = self.folder.restrictedTraverse('@@plone.app.tiles.demo.persistent/tile1')
        ITileDataManager(tile1).set({'message': u"First message", 'counter': 1})
        notify(ObjectAddedEvent(tile1, self.folder, 'tile1'))
        
        # Also create two other tiles, for control purposes
        tile2 = self.folder.restrictedTraverse('@@plone.app.tiles.demo.persistent/tile2')
        ITileDataManager(tile2).set({'message': u"Second message", 'counter': 2})
        notify(ObjectAddedEvent(tile2, self.folder, 'tile2'))
        
        tile3 = self.folder.restrictedTraverse('@@plone.app.tiles.demo.transient/tile3')
        ITileDataManager(tile3).set({'message': u"Third message"})
        notify(ObjectAddedEvent(tile3, self.folder, 'tile3'))
        
        # And some other tiles in another context
        tile2a = self.portal.restrictedTraverse('@@plone.app.tiles.demo.persistent/tile2')
        ITileDataManager(tile2a).set({'message': u"Second message", 'counter': 2})
        notify(ObjectAddedEvent(tile2a, self.portal, 'tile2'))
        
        tile4a = self.portal.restrictedTraverse('@@plone.app.tiles.demo.persistent/tile4')
        ITileDataManager(tile4a).set({'message': u"Fourth message", 'counter': 4})
        notify(ObjectAddedEvent(tile4a, self.portal, 'tile4'))
        
        # Find the tiles again using ITileBookkeeping
        bookkeeping = ITileBookkeeping(self.folder)
        
        self.assertEquals([('tile1', 'plone.app.tiles.demo.persistent'), ('tile2', 'plone.app.tiles.demo.persistent'), ('tile3', 'plone.app.tiles.demo.transient')],
                            sorted(list(bookkeeping.enumerate())))
        self.assertEquals([('tile1', 'plone.app.tiles.demo.persistent'), ('tile2', 'plone.app.tiles.demo.persistent')],
                            sorted(list(bookkeeping.enumerate('plone.app.tiles.demo.persistent'))))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile1'))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile2'))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile3'))
        
        # Let's say we found 'tile1' in the enumeration list and we realised
        # this tile was "lost" (e.g. no longer part of any valid page or site
        # layout). If we wanted to clean up its data, we could now do this:
        
        lostTileId = 'tile1'
        
        lostTileType = bookkeeping.typeOf(lostTileId)
        lostTileInstance = self.folder.restrictedTraverse('@@%s/%s' % (lostTileType, lostTileId,))
        ITileDataManager(lostTileInstance).delete()
        notify(ObjectRemovedEvent(lostTileInstance, self.folder, lostTileId))
        
        # Verify that the tile we wanted to remove is gone
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent'), ('tile3', 'plone.app.tiles.demo.transient')],
                            sorted(list(bookkeeping.enumerate())))
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent')],
                            sorted(list(bookkeeping.enumerate('plone.app.tiles.demo.persistent'))))
        self.assertEquals(None, bookkeeping.typeOf('tile1'))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile2'))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile3'))
        
        # Our other tiles are untouched
        bookkeeping = ITileBookkeeping(self.portal)
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent'), ('tile4', 'plone.app.tiles.demo.persistent')], sorted(list(bookkeeping.enumerate())))
    
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
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile1'))
        
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
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile1'))
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.transient/tile1?message=New+message')
        self.assertEquals("<html><body><b>Transient tile New message</b></body></html>", self.browser.contents)
        
        # Remove the tile
        self.browser.open(self.folder.absolute_url() + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.transient']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.transient', self.browser.getControl(name='deleted.type').value)
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([], list(bookkeeping.enumerate()))
        self.assertEquals([], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals(None, bookkeeping.typeOf('tile1'))
        
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
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile2'))
        
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
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile2', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile2'))
        
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
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([], list(bookkeeping.enumerate()))
        self.assertEquals([], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, bookkeeping.typeOf('tile2'))
        
        # Return to the content object
        self.browser.getControl(label='OK').click()
        self.assertEquals(self.folder.absolute_url() + '/view', self.browser.url)
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
