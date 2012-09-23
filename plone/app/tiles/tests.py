import urllib

import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING

from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations

from plone.tiles.data import ANNOTATIONS_KEY_PREFIX

from plone.app.drafts.interfaces import IDraftStorage
from plone.app.drafts.interfaces import PATH_KEY, DRAFT_NAME_KEY, TARGET_KEY
from plone.app.tiles.demo import TransientTile


class FunctionalTest(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def test_restrictedTraverse(self):
        portal = self.layer['portal']
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False

        # The easiest way to look up a tile in Zope 2 is to use traversal:

        traversed = portal.restrictedTraverse(
            '@@plone.app.tiles.demo.transient/tile-1')
        self.failUnless(isinstance(traversed, TransientTile))
        self.assertEquals('plone.app.tiles.demo.transient', traversed.__name__)
        self.assertEquals('tile-1', traversed.id)

    def test_transient_lifecycle(self):
        portal = self.layer['portal']
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False

        browser.addHeader(
            'Authorization',
            'Basic %s:%s' %
            (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

        # Add a new transient tile using the @@add-tile view
        browser.open(portal.absolute_url() + '/@@add-tile')
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.transient']
        # browser.getControl(name='id').value = "tile1"
        browser.getControl(name='form.button.Create').click()

        # Fill in the data and save. Note that the URL for the edit
        # form uses a `_tiledata` JSON argument to avoid collisions
        # between raw form data and tile data.
        browser.getControl(name='plone.app.tiles.demo.transient.message')\
            .value = 'Test message'
        browser.getControl(label='Save').click()

        self.assertEquals(portal.absolute_url() +
                          '/@@edit-tile/plone.app.tiles.demo.transient/tile' +
                          '-1?_tiledata=%7B%22message%22:%20%22Test%20messa' +
                          'ge%22%7D&tiledata=%7B%22action%22%3A%20%22save%22' +
                          '%2C%20%22url%22%3A%20%22./%40%40plone.app.tiles.' +
                          'demo.transient/tile-1%3Fmessage%3DTest%2Bmessage' +
                          '%22%2C%20%22tile_type%22%3A%20%22plone.app.tiles.' +
                          'demo.transient%22%2C%20%22mode%22%3A%20%22add%22' +
                          '%2C%20%22id%22%3A%20%22tile-1%22%7D',
                          browser.url)

        # View the tile
        browser.open(
            portal.absolute_url() +
            '/@@plone.app.tiles.demo.transient/tile-11' +
            '?message=Test+message')
        self.failUnless("<b>Transient tile Test message</b>" in
                        browser.contents)

        # Edit the tile
        browser.open(
            portal.absolute_url() +
            '/@@edit-tile/plone.app.tiles.demo.transient/' +
            'tile-1?message=Test+message')
        browser.getControl(
            name='plone.app.tiles.demo.transient.message').value = \
            'New message'
        browser.getControl(label='Save').click()

        self.assertEquals(portal.absolute_url() +
                          '/@@edit-tile/plone.app.tiles.demo.transient/' +
                          'tile-1?_tiledata=%7B%22message%22:%20%22New%20' +
                          'message%22%7D&tiledata=%7B%22action%22%3A%20%22' +
                          'save%22%2C%20%22url%22%3A%20%22./%40%40plone.' +
                          'app.tiles.demo.transient/tile-1%3Fmessage%3DNew' +
                          '%2Bmessage%22%2C%20%22tile_type%22%3A%20%22' +
                          'plone.app.tiles.demo.transient%22%2C%20%22mode' +
                          '%22%3A%20%22edit%22%2C%20%22id%22%3A%20%22tile' +
                          '-1%22%7D',
                          browser.url)

        # View the tile
        browser.open(
            portal.absolute_url() +
            '/@@plone.app.tiles.demo.transient/tile-1?message=New+message')
        self.assertEquals(
            "<html><body><b>Transient tile New message</b></body></html>",
            browser.contents)

        # Remove the tile
        browser.open(portal.absolute_url() + '/@@delete-tile')
        browser.getControl(name='id').value = 'tile-1'
        browser.getControl(name='type').value = [
            'plone.app.tiles.demo.transient']
        browser.getControl(name='confirm').click()

        self.assertEquals('tile-1',
                          browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.transient',
                          browser.getControl(name='deleted.type').value)

        # Return to the content object
        browser.getControl(label='OK').click()
        self.assertEquals(portal.absolute_url() + '/view',
                          browser.url)

    def test_persistent_lifecycle(self):
        portal = self.layer['portal']
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False

        folderAnnotations = IAnnotations(portal)
        annotationsKey = "%s.tile-1" % ANNOTATIONS_KEY_PREFIX

        self.assertEquals(None, folderAnnotations.get(annotationsKey))

        # Log in
        browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

        # Add a new persistent tile using the @@add-tile view
        browser.open(portal.absolute_url() + '/@@add-tile')
        browser.getControl(name='tiletype').value = [
            'plone.app.tiles.demo.persistent']
        # browser.getControl(name='id').value = "tile-1"
        browser.getControl(name='form.button.Create').click()

        # Fill in the data and save
        browser.getControl(
            name='plone.app.tiles.demo.persistent.message')\
            .value = 'Test message'
        browser.getControl(
            name='plone.app.tiles.demo.persistent.counter').value = '1'
        browser.getControl(label='Save').click()

        self.assertEquals(
            portal.absolute_url() +
            '/@@edit-tile/plone.app.tiles.demo.persistent/' +
            'tile-1?tiledata=%7B%22action%22%3A%20%22save' +
            '%22%2C%20%22url%22%3A%20%22./%40%40plone.app.' +
            'tiles.demo.persistent/tile-1%22%2C%20%22tile_' +
            'type%22%3A%20%22plone.app.tiles.demo.persistent' +
            '%22%2C%20%22mode%22%3A%20%22add%22%2C%20%22id' +
            '%22%3A%20%22tile-1%22%7D',
            browser.url)

        # Verify annotations
        self.assertEquals('Test message',
                          folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])

        # View the tile
        browser.open(
            portal.absolute_url() +
            '/@@plone.app.tiles.demo.persistent/tile-1')
        self.assertEquals(
            "<html><body><b>Persistent tile Test message #1</b></body></html>",
            browser.contents)

        # Edit the tile
        browser.open(
            portal.absolute_url() +
            '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        browser.getControl(
            name='plone.app.tiles.demo.transient.message')\
            .value = 'New message'
        browser.getControl(label='Save').click()

        self.assertEquals(
            portal.absolute_url() +
            '/@@edit-tile/plone.app.tiles.demo.persistent/' +
            'tile-1?tiledata=%7B%22action%22%3A%20%22save' +
            '%22%2C%20%22url%22%3A%20%22./%40%40plone.app.' +
            'tiles.demo.persistent/tile-1%22%2C%20%22' +
            'tile_type%22%3A%20%22plone.app.tiles.demo.' +
            'persistent%22%2C%20%22mode%22%3A%20%22edit' +
            '%22%2C%20%22id%22%3A%20%22tile-1%22%7D',
            browser.url)

        # Verify annotations
        self.assertEquals('New message',
                          folderAnnotations[annotationsKey]['message'])
        self.assertEquals(1, folderAnnotations[annotationsKey]['counter'])

        # View the tile
        browser.open(
            portal.absolute_url() +
            '/@@plone.app.tiles.demo.persistent/tile-1')
        self.assertEquals(
            "<html><body><b>Persistent tile New message #1</b></body></html>",
            browser.contents)

        # Remove the tile
        browser.open(portal.absolute_url() + '/@@delete-tile')
        browser.getControl(name='id').value = 'tile-1'
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='confirm').click()

        self.assertEquals('tile-1',
                          browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent',
                          browser.getControl(name='deleted.type').value)

        # Verify annotations
        self.assertEquals(None, folderAnnotations.get(annotationsKey))

        # Return to the content object
        browser.getControl(label='OK').click()
        self.assertEquals(portal.absolute_url() + '/view',
                          browser.url)

    # XXX: This test is failing. The cookies part of the headers read
    # by the browser is broken. The cookies are not extracted correctly
    # from the response.
    # The cookie reading works in the zope.testbrowser tests, but there
    # the response is a zope.publiser httpresponse, while ours is a
    # ZPublisher.HTTPResponse (older). So this might be a testbrowser
    # zope 2 integration bug.
    def test_persistent_drafting(self):
        portal = self.layer['portal']
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False

        folderAnnotations = IAnnotations(portal)
        annotationsKey = "%s.tile-1" % ANNOTATIONS_KEY_PREFIX

        drafts = getUtility(IDraftStorage)

        #
        # Step 0 - Log in
        #

        # Log in
        browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

        #
        # Step 1 - Create a new document and add, edit, remove and re-add tiles
        #

        # Open the add form for a Document

        browser.open(
            portal.absolute_url() +
            '/createObject?type_name=Document')

        editFormURL = browser.url
        baseURL = '/'.join(editFormURL.split('/')[:-1])

        # Get the values of the drafting cookies

        cookies = browser.cookies.forURL(baseURL)

        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        self.assertEquals(baseURL, 'http://nohost' + cookiePath)

        # Open the URL for the tile add view in this context. This simulates
        # an AJAX request for the same e.g. in a pop-up dialogue box

        browser.open(baseURL + '/@@add-tile')
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='form.button.Create').click()

        # Fill in the data and save
        browser.getControl(name='plone.app.tiles.demo.persistent.message')\
            .value = 'Test message'
        browser.getControl(
            name='plone.app.tiles.demo.persistent.counter').value = '1'
        browser.getControl(label='Save').click()

        # We should now have a draft for this item with the relevant
        # annotations

        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'] \
                        .replace('"', ''))

        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The saved data should be on the draft, and not on the container

        self.failIf(annotationsKey in folderAnnotations)
        self.failUnless(annotationsKey in draftAnnotations)

        self.assertEquals('Test message',
                          draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])

        # Edit the tile, still on the add form
        browser.open(baseURL + \
            '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')
        browser.getControl(name='plone.app.tiles.demo.persistent.message').value = 'New message'
        browser.getControl(label='Save').click()

        # Verify annotations
        self.assertEquals('New message',
                          draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])

        # Remove the tile
        browser.open(baseURL + '/@@delete-tile')
        browser.getControl(name='id').value = 'tile-1'
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='confirm').click()

        self.assertEquals('tile-1',
                          browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent',
                          browser.getControl(name='deleted.type').value)

        # Verify annotations
        self.assertEquals(None, draftAnnotations.get(annotationsKey))

        # Add a new tile
        browser.open(baseURL + '/@@add-tile')
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='form.button.Create').click()

        browser.getControl(name='plone.app.tiles.demo.persistent.message').value = 'Test message'
        browser.getControl(name='plone.app.tiles.demo.persistent.counter').value = '1'
        browser.getControl(label='Save').click()

        # Save the edit form

        browser.open(editFormURL)
        browser.getControl(name='title').value = u"New title"
        browser.getControl(name='form.button.save').click()

        # The cookies should now have all expired
        cookies = browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        # The draft should have disappeared

        self.assertEquals(None, drafts.getDraft(SITE_OWNER_NAME, targetKey,
                                                draftName))

        #
        # Step 2 - Edit the content object and a tile, but cancel
        #

        baseURL = browser.url
        editFormURL = baseURL + '/edit'

        annotationsKey = "%s.tile-2" % ANNOTATIONS_KEY_PREFIX

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        browser.open(editFormURL)

        # Get the values of the drafting cookies

        cookies = browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'] \
                        .replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'] \
                        .replace('"', ''))
        draftName = None

        self.assertEquals(baseURL, 'http://nohost' + cookiePath)

        self.assertEquals(0,
                          len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        # Edit the tile
        browser.open(baseURL + \
            '/@@edit-tile/plone.app.tiles.demo.persistent/tile-2')
        browser.getControl(name='plone.app.tiles.demo.persisten.message').value = 'Third message'
        browser.getControl(label='Save').click()

        # A draft should now have been created

        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'] \
                        .replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The data should have been updated on the draft, but not the context

        self.assertEquals('Third message',
                          draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])

        self.assertEquals('Test message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # Cancel editing

        # XXX: works around testbrowser/AT cancel button integration bug
        browser.open(baseURL)
        browser.getLink('Edit').click()
        browser.getControl(name='form.button.cancel').click()

        # Verify that the tile data has not been copied to the context

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEquals('Test message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should be discarded, too

        cookies = browser.cookies.forURL(baseURL)
        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEquals(0,
                          len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 3 - Edit the content object and save
        #

        browser.getLink('Edit').click()

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'] \
                        .replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'] \
                        .replace('"', ''))
        draftName = None

        # Edit the tile
        browser.open(baseURL + \
            '/@@edit-tile/plone.app.tiles.demo.persistent/tile-2')
        browser.getControl(name='message').value = 'Third message'
        browser.getControl(label='Save').click()

        # A draft should now have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'] \
                        .replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The data should have been updated on the draft, but not the context
        self.assertEquals('Third message',
                          draftAnnotations[annotationsKey]['message'])
        self.assertEquals(1, draftAnnotations[annotationsKey]['counter'])

        self.assertEquals('Test message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # Save the edit form
        browser.open(editFormURL)
        browser.getControl(name='form.button.save').click()

        # Verify that the tile has been updated
        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEquals('Third message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should have been discarded as well
        cookies = browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEquals(0,
                          len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 4 - Edit the content object, remove the tile, but cancel
        #

        browser.getLink('Edit').click()

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'] \
                        .replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'] \
                        .replace('"', ''))
        draftName = None

        # Remove the tile

        browser.open(baseURL + '/@@delete-tile')
        browser.getControl(name='id').value = 'tile-2'
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='confirm').click()

        self.assertEquals('tile-2',
                          browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent',
                          browser.getControl(name='deleted.type').value)

        # Draft should have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'] \
                        .replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # Verify that the deletion has happened on the draft (only)

        self.assertEquals(None, draftAnnotations.get(annotationsKey))
        self.assertEquals(set([u'plone.tiles.data.tile-2']),
                          draft._proxyAnnotationsDeleted)

        self.assertEquals('Third message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # Cancel editing
        # XXX: works around testbrowser/AT cancel button integration bug
        browser.open(baseURL)
        browser.getLink('Edit').click()
        browser.getControl(name='form.button.cancel').click()

        # Verify that the tile has not been deleted on the context

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEquals('Third message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should have been discarded as well
        cookies = browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEquals(0,
                          len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 5 - Edit the content object, remove the tile, and save
        #

        browser.getLink('Edit').click()

        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(cookies['plone.app.drafts.targetKey'] \
                        .replace('"', ''))
        cookiePath = urllib.unquote(cookies['plone.app.drafts.path'] \
                        .replace('"', ''))
        draftName = None

        # Remove the tile

        browser.open(baseURL + '/@@delete-tile')
        browser.getControl(name='id').value = 'tile-2'
        browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        browser.getControl(name='confirm').click()

        self.assertEquals('tile-2',
                          browser.getControl(name='deleted.id').value)
        self.assertEquals('plone.app.tiles.demo.persistent',
                          browser.getControl(name='deleted.type').value)

        # Draft should have been created
        draftName = urllib.unquote(cookies['plone.app.drafts.draftName'] \
                        .replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # Verify that the deletion has happened on the draft (only)

        self.assertEquals(None, draftAnnotations.get(annotationsKey))

        self.assertEquals(set([u'plone.tiles.data.tile-2']),
                          draft._proxyAnnotationsDeleted)

        self.assertEquals('Third message',
                          contextAnnotations[annotationsKey]['message'])
        self.assertEquals(1, contextAnnotations[annotationsKey]['counter'])

        # Save the edit form
        browser.open(editFormURL)
        browser.getControl(name='form.button.save').click()

        # Verify that the tile is now actually removed
        context = portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEquals(None, contextAnnotations.get(annotationsKey))

        # The draft should have been discarded as well
        cookies = browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEquals(0,
                          len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))
