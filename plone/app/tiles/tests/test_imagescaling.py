# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.tiles.demo import PersistentTile
from plone.app.tiles.testing import PLONE_APP_TILES_INTEGRATION_TESTING
from plone.namedfile.file import NamedImage
from plone.namedfile.tests import getFile
from plone.tiles.interfaces import ITileDataManager

import six
import unittest


class MockNamedImage(NamedImage):
    _p_mtime = DateTime().millis()


class TestImageScaling(unittest.TestCase):

    layer = PLONE_APP_TILES_INTEGRATION_TESTING

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

    def testImageScaling(self):
        tile = PersistentTile(self.portal, self.request)
        tile.id = "mytile"
        data = getFile("image.png")
        data = {
            "message": u"foo",
            "image": MockNamedImage(data, "image/png", u"image.png"),
        }
        dm = ITileDataManager(tile)
        dm.set(data)

        images = self.portal.restrictedTraverse(
            "@@plone.app.tiles.demo.persistent/mytile/@@images"
        )
        if six.PY2:
            assertRegex = self.assertRegexpMatches
        else:
            assertRegex = self.assertRegex

        assertRegex(
            images.tag("image", width=10),
            r'<img src="http://nohost/plone/@@plone.app.tiles.demo.persistent/mytile/@@images/[a-z0-9-]+\.png" '
            r'alt="foo" title="foo" height="10" width="10" />',
        )

        scale = images.scale("image", scale="mini")
        self.assertEqual(scale.data.data[:4], b"\x89PNG")
        self.assertEqual(scale.data.getImageSize(), (200, 200))
        assertRegex(
            scale.url,
            r"http://nohost/plone/@@plone.app.tiles.demo.persistent/mytile/@@images/[a-z0-9-]+\.png",
        )
