# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.tiles.demo import PersistentTile
from plone.app.tiles.testing import PLONE_APP_TILES_FUNCTIONAL_TESTING
from plone.app.tiles.testing import PLONE_APP_TILES_INTEGRATION_TESTING
from plone.namedfile.file import NamedImage
from plone.namedfile.tests import getFile
from plone.tiles.interfaces import ITileDataManager

import six
import transaction
import unittest

try:
    from plone.testing.zope import Browser
except ImportError:
    # BBB Plone 5.1
    from plone.testing.z2 import Browser


class MockNamedImage(NamedImage):
    _p_mtime = DateTime().millis()


class TestImageScaling(unittest.TestCase):
    layer = PLONE_APP_TILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        # we need to have the Manager role to be able to add things
        # to the portal root
        setRoles(
            self.portal,
            TEST_USER_ID,
            [
                "Manager",
            ],
        )
        self.tile = PersistentTile(self.portal, self.request)
        self.tile.id = "mytile"
        data = getFile("image.png")
        data = {
            "message": u"foo",
            "image": MockNamedImage(data, "image/png", u"image.png"),
            "image2": MockNamedImage(data, "image/png", u"image.png"),
        }
        dm = ITileDataManager(self.tile)
        dm.set(data)
        transaction.commit()

        app = self.layer["app"]
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        self.base_url = self.portal.absolute_url() + "/@@plone.app.tiles.demo.persistent/mytile"

    def testImageScaling(self):
        images = self.portal.restrictedTraverse(
            "@@plone.app.tiles.demo.persistent/mytile/@@images"
        )
        if six.PY2:
            assertRegex = self.assertRegexpMatches
        else:
            assertRegex = self.assertRegex

        # Test the tag method.
        assertRegex(
            images.tag("image", width=10),
            r'<img src="http://nohost/plone/@@plone.app.tiles.demo.persistent/mytile/@@images/[a-z0-9-]+\.png" '
            r'alt="foo" title="foo" height="10" width="10" />',
        )

        # Test the scale method.
        scale = images.scale("image", scale="mini")
        self.assertEqual(scale.data.data[:4], b"\x89PNG")
        self.assertEqual(scale.data.getImageSize(), (200, 200))
        assertRegex(
            scale.url,
            r"http://nohost/plone/@@plone.app.tiles.demo.persistent/mytile/@@images/[a-z0-9-]+\.png",
        )
        transaction.commit()

        # Visit the unique scale in the browser.
        self.browser.open(scale.url)
        self.assertEqual(self.browser.contents, scale.data.data)

        # Visit the general scale in the browser.
        self.browser.open(self.base_url + "/@@images/image/mini")
        self.assertEqual(self.browser.contents, scale.data.data)

    def test_browse_scale(self):
        self.browser.open(self.base_url + "/@@images/image/thumb")

    def test_browse_original_with_property(self):
        # On the tile we have explicitly defined an image property,
        # which is why the following has always worked.
        self.browser.open(self.base_url + "/@@images/image")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)

    def test_browse_original_without_property(self):
        # For the second image we have *not* explicitly defined an image property
        # on the tile, so getting the original failed for a long time.
        self.browser.open(self.base_url + "/@@images/image2")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)

    def test_download_original_with_property(self):
        # On the tile we have explicitly defined an image property.
        self.browser.open(self.base_url + "/@@download/image")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)

    def test_download_original_without_property(self):
        self.browser.open(self.base_url + "/@@download/image2")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)

    def test_display_file_with_property(self):
        self.browser.open(self.base_url + "/@@display-file/image")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)

    def test_display_file_without_property(self):
        self.browser.open(self.base_url + "/@@display-file/image2")
        orig = getFile("image.png")
        if hasattr(orig, "read"):
            # BBB Plone 5.1: it is an open file, not bytes.
            orig = orig.read()
        self.assertEqual(self.browser.contents, orig)
