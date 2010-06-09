import urllib

import unittest
from zope.testing import doctest

from Products.PloneTestCase import ptc
from Products.Five import zcml
from Products.Five.testbrowser import Browser

import collective.testcaselayer.ptc

import plone.app.tiles

from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent

from zope.annotation.interfaces import IAnnotations

from plone.tiles.interfaces import ITileDataManager
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX

from plone.app.drafts.interfaces import IDraftStorage

from plone.app.tiles.interfaces import ITileBookkeeping
from plone.app.tiles.demo import TransientTile

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):
    
    def afterSetUp(self):
        zcml.load_config('configure.zcml', plone.app.tiles)
        zcml.load_config('demo.zcml', plone.app.tiles)
        
        self.addProfile('plone.app.tiles:default')


Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class FunctionalTest(ptc.FunctionalTestCase):
    
    layer = Layer

    def afterSetUp(self):
        self.browser = Browser()
        self.browser.handleErrors = False
    
    def test_restrictedTraverse(self):
        
        # The easiest way to look up a tile in Zope 2 is to use traversal:
        
        traversed = self.portal.restrictedTraverse('@@plone.app.tiles.demo.transient/tile-1')
        self.failUnless(isinstance(traversed, TransientTile))
        self.assertEquals('plone.app.tiles.demo.transient', traversed.__name__)
        self.assertEquals('tile-1', traversed.id)
    
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
        
        self.assertEquals(3, bookkeeping.counter())
        
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
        
        # The counter is not decremented on remove
        self.assertEquals(2, bookkeeping.counter())
    
    def test_transient_lifecycle(self):
        # Log in
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (ptc.default_user, ptc.default_password,))
        
        # Add a new transient tile using the @@add-tile view
        self.browser.open(self.folder.absolute_url() + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.transient']
        # self.browser.getControl(name='id').value = "tile1"
        self.browser.getControl(name='form.button.Create').click()
        
        # Fill in the data and save
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile-1?message=Test+message&' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22./%40%40plone.app.tiles.demo.transient/tile-1%3Fmessage%3DTest%2Bmessage%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.transient%22%2C%20%22mode%22%3A%20%22add%22%2C%20%22id%22%3A%20%22tile-1%22%7D',
                          self.browser.url)
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.transient/tile-11?message=Test+message')
        self.assertEquals("<html><body><b>Transient tile Test message</b></body></html>", self.browser.contents)
        
        # Edit the tile
        self.browser.open(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile-1?message=Test+message')
        self.browser.getControl(name='message').value = 'New message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile-1?message=New+message&' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22./%40%40plone.app.tiles.demo.transient/tile-1%3Fmessage%3DNew%2Bmessage%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.transient%22%2C%20%22mode%22%3A%20%22edit%22%2C%20%22id%22%3A%20%22tile-1%22%7D',
                          self.browser.url)
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.transient')], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals('plone.app.tiles.demo.transient', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.transient/tile-1?message=New+message')
        self.assertEquals("<html><body><b>Transient tile New message</b></body></html>", self.browser.contents)
        
        # Remove the tile
        self.browser.open(self.folder.absolute_url() + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.transient']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile-1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.transient', self.browser.getControl(name='deleted.type').value)
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([], list(bookkeeping.enumerate()))
        self.assertEquals([], list(bookkeeping.enumerate('plone.app.tiles.demo.transient')))
        self.assertEquals(None, bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # Return to the content object
        self.browser.getControl(label='OK').click()
        self.assertEquals(self.folder.absolute_url() + '/view', self.browser.url)
    
    def test_persistent_lifecycle(self):
        
        folderAnnotations = IAnnotations(self.folder)
        annotationsKey = "%s.tile-1" % ANNOTATIONS_KEY_PREFIX
        
        self.assertEquals(None, folderAnnotations.get(annotationsKey))
        
        # Log in
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (ptc.default_user, ptc.default_password,))
        
        # Add a new persistent tile using the @@add-tile view
        self.browser.open(self.folder.absolute_url() + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        # self.browser.getControl(name='id').value = "tile-1"
        self.browser.getControl(name='form.button.Create').click()
        
        # Fill in the data and save
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(name='counter').value = '1'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1?' + \
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22./%40%40plone.app.tiles.demo.persistent/tile-1%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.persistent%22%2C%20%22mode%22%3A%20%22add%22%2C%20%22id%22%3A%20%22tile-1%22%7D',
                          self.browser.url)
        
        # Verify annotations
        self.assertEquals('Test message', folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.persistent/tile-1')
        self.assertEquals("<html><body><b>Persistent tile Test message #1</b></body></html>", self.browser.contents)
        
        # Edit the tile
        self.browser.open(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        self.browser.getControl(name='message').value = 'New message'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals(self.folder.absolute_url() + \
                          '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1?' +
                          'tiledata=%7B%22action%22%3A%20%22save%22%2C%20%22url%22%3A%20%22./%40%40plone.app.tiles.demo.persistent/tile-1%22%2C%20%22type%22%3A%20%22plone.app.tiles.demo.persistent%22%2C%20%22mode%22%3A%20%22edit%22%2C%20%22id%22%3A%20%22tile-1%22%7D',
                          self.browser.url)
        
        # Verify annotations
        self.assertEquals('New message', folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # View the tile
        self.browser.open(self.folder.absolute_url() + '/@@plone.app.tiles.demo.persistent/tile-1')
        self.assertEquals("<html><body><b>Persistent tile New message #1</b></body></html>", self.browser.contents)
        
        # Remove the tile
        self.browser.open(self.folder.absolute_url() + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile-1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent', self.browser.getControl(name='deleted.type').value)
        
        # Verify annotations
        self.assertEquals(None, folderAnnotations.get(annotationsKey))
        
        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(self.folder)
        self.assertEquals([], list(bookkeeping.enumerate()))
        self.assertEquals([], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # Return to the content object
        self.browser.getControl(label='OK').click()
        self.assertEquals(self.folder.absolute_url() + '/view', self.browser.url)
    
    def test_persistent_drafting(self):
        
        folderAnnotations = IAnnotations(self.folder)
        annotationsKey = "%s.tile-1" % ANNOTATIONS_KEY_PREFIX
        
        drafts = getUtility(IDraftStorage)
        
        #
        # Step 0 - Log in
        # 
        
        # Log in
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (ptc.default_user, ptc.default_password,))
        
        #
        # Step 1 - Create a new document and add, edit, remove and re-add tiles
        # 
        
        # Open the add form for a Document
        
        self.browser.open(self.folder.absolute_url() + '/createObject?type_name=Document')
        
        editFormURL = self.browser.url
        baseURL = '/'.join(editFormURL.split('/')[:-1])
        
        # Get the values of the drafting cookies
        
        cookies = self.browser.cookies.forURL(baseURL)
        
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None
        
        self.assertEquals(baseURL, 'http://nohost' + cookiePath)
        
        # Open the URL for the tile add view in this context. This simulates
        # an AJAX request for the same e.g. in a pop-up dialogue box
        
        self.browser.open(baseURL + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='form.button.Create').click()

        # Fill in the data and save
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(name='counter').value = '1'
        self.browser.getControl(label='Save').click()
        
        # We should now have a draft for this item with the relevant
        # annotations and book-keeping info
        
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'].replace('"', ''))
        
        draft = drafts.getDraft(ptc.default_user, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)
        
        # The saved data should be on the draft, and not on the container
        
        self.failIf(annotationsKey in folderAnnotations)
        self.failUnless(annotationsKey in draftAnnotations)
        
        self.assertEquals('Test message', draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])
         
        # Check bookkeeping information, also on the draft
        bookkeeping = ITileBookkeeping(draft)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # Edit the tile, still on the add form
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        self.browser.getControl(name='message').value = 'New message'
        self.browser.getControl(label='Save').click()
        
        # Verify annotations
        self.assertEquals('New message', draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])

        # Check bookkeeping information
        bookkeeping = ITileBookkeeping(draft)
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())
        
        # Remove the tile
        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile-1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent', self.browser.getControl(name='deleted.type').value)
        
        # Verify annotations
        self.assertEquals(None, draftAnnotations.get(annotationsKey))
        
        # Check bookkeeping information
        self.assertEquals([], list(bookkeeping.enumerate()))
        self.assertEquals([], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, bookkeeping.typeOf('tile-1'))
        self.assertEquals(1, bookkeeping.counter())

        # Add a new tile
        self.browser.open(baseURL + '/@@add-tile')
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='form.button.Create').click()
        
        self.browser.getControl(name='message').value = 'Test message'
        self.browser.getControl(name='counter').value = '1'
        self.browser.getControl(label='Save').click()
        
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(bookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', bookkeeping.typeOf('tile-1'))
        self.assertEquals(2, bookkeeping.counter()) # counter always increments
        
        # Save the edit form
        
        self.browser.open(editFormURL)
        self.browser.getControl(name='title').value = u"New title"
        self.browser.getControl(name='form.button.save').click()
        
        # The cookies should now have all expired
        cookies = self.browser.cookies.forURL(baseURL)
        self.assertEquals(0, len(cookies))
        
        # Verify that the tile is there on the content object this time
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.assertEquals('Test message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter()) # counter always increments
        
        # The draft should have disappeared as well
        
        self.assertEquals(None, drafts.getDraft(ptc.default_user, targetKey, draftName))
        
        #
        # Step 2 - Edit the content object and a tile, but cancel
        # 
        
        baseURL = self.browser.url
        editFormURL = baseURL + '/edit'
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.browser.open(editFormURL)
        
        # Get the values of the drafting cookies
        
        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None
        
        self.assertEquals(baseURL, 'http://nohost' + cookiePath)
        
        self.assertEquals(0, len(drafts.getDrafts(ptc.default_user, targetKey)))
        
        # Edit the tile
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        self.browser.getControl(name='message').value = 'Third message'
        self.browser.getControl(label='Save').click()
        
        # A draft should now have been created
        
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(ptc.default_user, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)
        
        # The data should have been updated on the draft, but not the context
        
        self.assertEquals('Third message', draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])
        # The draft book-keeping information is not re-saved since we didn't
        # add or remove any tiles
        
        self.assertEquals('Test message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # Cancel editing
        
        # XXX: works around testbrowser/AT cancel button integration bug
        self.browser.open(baseURL)
        self.browser.getLink('Edit').click()
        self.browser.getControl(name='form.button.cancel').click()
        
        # Verify that the tile data has not been copied to the context
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.assertEquals('Test message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # The draft should be discarded, too
        
        cookies = self.browser.cookies.forURL(baseURL)
        self.assertEquals(0, len(cookies))
        self.assertEquals(0, len(drafts.getDrafts(ptc.default_user, targetKey)))
        
        #
        # Step 3 - Edit the content object and save
        # 
        
        self.browser.getLink('Edit').click()
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None
        
        # Edit the tile
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        self.browser.getControl(name='message').value = 'Third message'
        self.browser.getControl(label='Save').click()
        
        # A draft should now have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(ptc.default_user, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)
        
        # The data should have been updated on the draft, but not the context
        self.assertEquals('Third message', draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])
        
        self.assertEquals('Test message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # Save the edit form
        self.browser.open(editFormURL)
        self.browser.getControl(name='form.button.save').click()
        
        # Verify that the tile has been updated
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.assertEquals('Third message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)
        self.assertEquals(0, len(cookies))
        self.assertEquals(0, len(drafts.getDrafts(ptc.default_user, targetKey)))
        
        #
        # Step 4 - Edit the content object, remove the tile, but cancel
        # 
        
        self.browser.getLink('Edit').click()
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None
        
        # Remove the tile
        
        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile-1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent', self.browser.getControl(name='deleted.type').value)
        
        # Draft should have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(ptc.default_user, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)
        draftBookkeeping = ITileBookkeeping(draft)
        
        # Verify that the deletion has happened on the draft (only)
        
        self.assertEquals(None, draftAnnotations.get(annotationsKey))
        self.assertEquals([], list(draftBookkeeping.enumerate()))
        self.assertEquals([], list(draftBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, draftBookkeeping.typeOf('tile-1'))
        
        self.assertEquals(set([u'plone.tiles.data.tile-1']), draft._proxyAnnotationsDeleted)
        
        self.assertEquals('Third message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # Cancel editing
        # XXX: works around testbrowser/AT cancel button integration bug
        self.browser.open(baseURL)
        self.browser.getLink('Edit').click()
        self.browser.getControl(name='form.button.cancel').click()
        
        # Verify that the tile has not been deleted on the context
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.assertEquals('Third message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)
        self.assertEquals(0, len(cookies))
        self.assertEquals(0, len(drafts.getDrafts(ptc.default_user, targetKey)))
        
        #
        # Step 5 - Edit the content object, remove the tile, and save
        # 
        
        self.browser.getLink('Edit').click()
        
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None
        
        # Remove the tile
        
        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='type').value = ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()
        
        self.assertEquals('tile-1', self.browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent', self.browser.getControl(name='deleted.type').value)
        
        # Draft should have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(ptc.default_user, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)
        draftBookkeeping = ITileBookkeeping(draft)
        
        # Verify that the deletion has happened on the draft (only)
        
        self.assertEquals(None, draftAnnotations.get(annotationsKey))
        self.assertEquals([], list(draftBookkeeping.enumerate()))
        self.assertEquals([], list(draftBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, draftBookkeeping.typeOf('tile-1'))
        
        self.assertEquals(set([u'plone.tiles.data.tile-1']), draft._proxyAnnotationsDeleted)
        
        self.assertEquals('Third message', contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate()))
        self.assertEquals([('tile-1', 'plone.app.tiles.demo.persistent')], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals('plone.app.tiles.demo.persistent', contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # Save the edit form
        self.browser.open(editFormURL)
        self.browser.getControl(name='form.button.save').click()
        
        # Verify that the tile is now actually removed
        context = self.folder['new-title']
        contextAnnotations = IAnnotations(context)
        contextBookkeeping = ITileBookkeeping(context)
        
        self.assertEquals(None, contextAnnotations.get(annotationsKey))
        self.assertEquals([], list(contextBookkeeping.enumerate()))
        self.assertEquals([], list(contextBookkeeping.enumerate('plone.app.tiles.demo.persistent')))
        self.assertEquals(None, contextBookkeeping.typeOf('tile-1'))
        self.assertEquals(2, contextBookkeeping.counter())
        
        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)
        self.assertEquals(0, len(cookies))
        self.assertEquals(0, len(drafts.getDrafts(ptc.default_user, targetKey)))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
