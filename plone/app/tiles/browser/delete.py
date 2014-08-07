# -*- coding: utf-8 -*-
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from zope.annotation.interfaces import IAnnotations
from Products.Five import BrowserView


class DefaultDeleteView(BrowserView):

    tileId = None

    def __init__(self, context, request, tileType):
        super(DefaultDeleteView, self).__init__(context, request)
        self.tileType = tileType
        self.annotations = IAnnotations(self.context)
        self.tileId = None

    def get_key(self):
        if self.tileId:
            return '%s.%s' % (
                ANNOTATIONS_KEY_PREFIX,
                self.tileId
            )
        return ''

    def __call__(self):
        self.deleted = False
        key = self.get_key()
        # XXX: Should we trigger a proper event here?
        # XXX: Is it useful outside the (removed?) book keeping system?
        if key and key in self.annotations.keys():
            del self.annotations[key]
            return True
        # return self.index()
        return False

    def tiles(self):
        for item in self.annotations.keys():
            if item.startswith(ANNOTATIONS_KEY_PREFIX):
                yield item[len(ANNOTATIONS_KEY_PREFIX) + 1:]
