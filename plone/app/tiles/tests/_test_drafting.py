# -*- coding: utf-8 -*-
import urllib
import pkg_resources
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX

try:
    pkg_resources.get_distribution('plone.app.drafts')
except pkg_resources.DistributionNotFound:
    HAS_DRAFTS = False
else:
    HAS_DRAFTS = True

if HAS_DRAFTS:
    from plone.app.drafts.interfaces import DRAFT_NAME_KEY
    from plone.app.drafts.interfaces import IDraftStorage
    from plone.app.drafts.interfaces import PATH_KEY
    from plone.app.drafts.interfaces import TARGET_KEY

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestTileDrafting(unittest.TestCase):

    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        app = self.layer['app']
        self.browser = Browser(app)
        self.browser.handleErrors = False

    # XXX: This test may be failing. The cookies part of the headers read
    # by the browser is broken. The cookies are not extracted correctly
    # from the response.
    # The cookie reading works in the zope.testbrowser tests, but there
    # the response is a zope.publiser httpresponse, while ours is a
    # ZPublisher.HTTPResponse (older). So this might be a testbrowser
    # zope 2 integration bug.
    def test_persistent_drafting(self):
        folderAnnotations = IAnnotations(self.portal)
        annotationsKey = "%s.tile-1" % ANNOTATIONS_KEY_PREFIX

        drafts = getUtility(IDraftStorage)

        #
        # Step 0 - Log in
        #

        # Log in
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

        #
        # Step 1 - Create a new document and add, edit, remove and re-add tiles
        #

        # Open the add form for a Document

        self.browser.open(
            self.portal_url +
            '/++add++Page')

        editFormURL = self.browser.url
        baseURL = '/'.join(editFormURL.split('/')[:-1])

        # Get the values of the drafting cookies

        cookies = self.browser.cookies.forURL(baseURL)

        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        self.assertEqual(baseURL, 'http://nohost' + cookiePath)

        # Open the URL for the tile add view in this context. This simulates
        # an AJAX request for the same e.g. in a pop-up dialogue box

        self.browser.open(baseURL + '/@@add-tile')
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='form.button.Create').click()

        # Fill in the data and save
        self.browser.getControl(name='plone.app.tiles.demo.persistent.message')\
            .value = 'Test message'
        self.browser.getControl(
            name='plone.app.tiles.demo.persistent.counter').value = '1'
        # XXX
        # XXX: This is as far we get with dexterit draft test
        # XXX: Next we should have a way to update draft instead
        # XXX: of saving the tile and not creating draft...
        # XXX
        self.browser.getControl(label='Save').click()

        # We should now have a draft for this item with the relevant
        # annotations

        draftName = urllib.unquote(
            cookies['plone.app.drafts.draftName'].replace('"', ''))

        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The saved data should be on the draft, and not on the container

        self.failIf(annotationsKey in folderAnnotations)
        self.failUnless(annotationsKey in draftAnnotations)

        self.assertEqual('Test message',
                         draftAnnotations[annotationsKey]['message'])
        self.assertEqual(1, draftAnnotations[annotationsKey]['counter'])

        # Edit the tile, still on the add form
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-1')  # noqa  # noqa  # noqa  # noqa  # noqa  # noqa  # noqa  # noqa  # noqa
        self.browser.getControl(name='plone.app.tiles.demo.persistent.message').value = 'New message'  # noqa
        self.browser.getControl(label='Save').click()

        # Verify annotations
        self.assertEqual('New message',
                         draftAnnotations[annotationsKey]['message'])
        self.assertEqual(1, draftAnnotations[annotationsKey]['counter'])

        # Remove the tile
        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-1'
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()

        self.assertEqual('tile-1',
                         self.browser.getControl(name='deleted.id').value)
        self.assertEqual('plone.app.tiles.demo.persistent',
                         self.browser.getControl(name='deleted.type').value)

        # Verify annotations
        self.assertEqual(None, draftAnnotations.get(annotationsKey))

        # Add a new tile
        self.browser.open(baseURL + '/@@add-tile')
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='form.button.Create').click()

        self.browser.getControl(name='plone.app.tiles.demo.persistent.message').value = 'Test message'  # noqa
        self.browser.getControl(name='plone.app.tiles.demo.persistent.counter').value = '1'  # noqa
        self.browser.getControl(label='Save').click()

        # Save the edit form

        self.browser.open(editFormURL)
        self.browser.getControl(name='title').value = u"New title"
        self.browser.getControl(name='form.button.save').click()

        # The cookies should now have all expired
        cookies = self.browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        # The draft should have disappeared

        self.assertEqual(None, drafts.getDraft(SITE_OWNER_NAME, targetKey,
                                               draftName))

        #
        # Step 2 - Edit the content object and a tile, but cancel
        #

        baseURL = self.browser.url
        editFormURL = baseURL + '/edit'

        annotationsKey = "%s.tile-2" % ANNOTATIONS_KEY_PREFIX

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.browser.open(editFormURL)

        # Get the values of the drafting cookies

        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        self.assertEqual(baseURL, 'http://nohost' + cookiePath)

        self.assertEqual(0,
                         len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        # Edit the tile
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-2')  # noqa
        self.browser.getControl(name='plone.app.tiles.demo.persisten.message').value = 'Third message'  # noqa
        self.browser.getControl(label='Save').click()

        # A draft should now have been created

        draftName = urllib.unquote(
            cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The data should have been updated on the draft, but not the context

        self.assertEqual('Third message',
                         draftAnnotations[annotationsKey]['message'])
        self.assertEqual(1, draftAnnotations[annotationsKey]['counter'])

        self.assertEqual('Test message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # Cancel editing

        # XXX: works around testbrowser/AT cancel button integration bug
        self.browser.open(baseURL)
        self.browser.getLink('Edit').click()
        self.browser.getControl(name='form.button.cancel').click()

        # Verify that the tile data has not been copied to the context

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEqual('Test message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should be discarded, too

        cookies = self.browser.cookies.forURL(baseURL)
        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEqual(0,
                         len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 3 - Edit the content object and save
        #

        self.browser.getLink('Edit').click()

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        # Edit the tile
        self.browser.open(baseURL + '/@@edit-tile/plone.app.tiles.demo.persistent/tile-2')  # noqa
        self.browser.getControl(name='message').value = 'Third message'
        self.browser.getControl(label='Save').click()

        # A draft should now have been created
        draftName = urllib.unquote(
            cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # The data should have been updated on the draft, but not the context
        self.assertEqual('Third message',
                         draftAnnotations[annotationsKey]['message'])
        self.assertEqual(1, draftAnnotations[annotationsKey]['counter'])

        self.assertEqual('Test message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # Save the edit form
        self.browser.open(editFormURL)
        self.browser.getControl(name='form.button.save').click()

        # Verify that the tile has been updated
        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEqual('Third message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEqual(0,
                         len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 4 - Edit the content object, remove the tile, but cancel
        #

        self.browser.getLink('Edit').click()

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        # Remove the tile

        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-2'
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()

        self.assertEqual('tile-2',
                         self.browser.getControl(name='deleted.id').value)
        self.assertEqual('plone.app.tiles.demo.persistent',
                         self.browser.getControl(name='deleted.type').value)

        # Draft should have been created
        draftName = urllib.unquote(
            cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # Verify that the deletion has happened on the draft (only)

        self.assertEqual(None, draftAnnotations.get(annotationsKey))
        self.assertEqual(set([u'plone.tiles.data.tile-2']),
                         draft._proxyAnnotationsDeleted)

        self.assertEqual('Third message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # Cancel editing
        # XXX: works around testbrowser/AT cancel button integration bug
        self.browser.open(baseURL)
        self.browser.getLink('Edit').click()
        self.browser.getControl(name='form.button.cancel').click()

        # Verify that the tile has not been deleted on the context

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEqual('Third message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEqual(0,
                         len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))

        #
        # Step 5 - Edit the content object, remove the tile, and save
        #

        self.browser.getLink('Edit').click()

        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        cookies = self.browser.cookies.forURL(baseURL)
        targetKey = urllib.unquote(
            cookies['plone.app.drafts.targetKey'].replace('"', ''))
        cookiePath = urllib.unquote(
            cookies['plone.app.drafts.path'].replace('"', ''))
        draftName = None

        # Remove the tile

        self.browser.open(baseURL + '/@@delete-tile')
        self.browser.getControl(name='id').value = 'tile-2'
        self.browser.getControl(name='tiletype').value = \
            ['plone.app.tiles.demo.persistent']
        self.browser.getControl(name='confirm').click()

        self.assertEqual('tile-2',
                         self.browser.getControl(name='deleted.id').value)
        self.assertEqual('plone.app.tiles.demo.persistent',
                         self.browser.getControl(name='deleted.type').value)

        # Draft should have been created
        draftName = urllib.unquote(
            cookies['plone.app.drafts.draftName'].replace('"', ''))
        draft = drafts.getDraft(SITE_OWNER_NAME, targetKey, draftName)
        draftAnnotations = IAnnotations(draft)

        # Verify that the deletion has happened on the draft (only)

        self.assertEqual(None, draftAnnotations.get(annotationsKey))

        self.assertEqual(set([u'plone.tiles.data.tile-2']),
                         draft._proxyAnnotationsDeleted)

        self.assertEqual('Third message',
                         contextAnnotations[annotationsKey]['message'])
        self.assertEqual(1, contextAnnotations[annotationsKey]['counter'])

        # Save the edit form
        self.browser.open(editFormURL)
        self.browser.getControl(name='form.button.save').click()

        # Verify that the tile is now actually removed
        context = self.portal['new-title']
        contextAnnotations = IAnnotations(context)

        self.assertEqual(None, contextAnnotations.get(annotationsKey))

        # The draft should have been discarded as well
        cookies = self.browser.cookies.forURL(baseURL)

        self.assertFalse(TARGET_KEY in cookies)
        self.assertFalse(DRAFT_NAME_KEY in cookies)
        self.assertFalse(PATH_KEY in cookies)

        self.assertEqual(0,
                         len(drafts.getDrafts(SITE_OWNER_NAME, targetKey)))
