# -*- coding: utf-8 -*-
from AccessControl.security import checkPermission
from zope.globalrequest import getRequest
from zope.component import getUtilitiesFor
from zope.interface import implementer
from zope.component import queryMultiAdapter
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from plone.tiles.interfaces import ITileType


@implementer(IVocabularyFactory)
class RegisteredTilesVocabulary(object):
    """Return vocabulary of all tiles registered"""

    def __init__(self, context=None):
        self.context = context

    def __call__(self, context=None):
        context = context or self.context

        items = []
        tiles = getUtilitiesFor(ITileType, context=context)
        for name, tile in tiles:
            items.append(SimpleTerm(tile, name, tile.title))
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AvailableTilesVocabulary(RegisteredTilesVocabulary):
    """Return vocabulary of all tiles with view for the context"""

    def __call__(self, context=None):
        context = context or self.context
        vocabulary = super(AvailableTilesVocabulary, self).__call__(context)
        request = getRequest()

        items = []
        for item in vocabulary:
            if queryMultiAdapter((context, request), name=item.token) is not None:  # noqa
                items.append(item)
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AllowedTilesVocabulary(AvailableTilesVocabulary):
    """Return vocabulary of all tiles with allowed add permission"""

    def __call__(self, context=None):
        context = self.context or context
        vocabulary = super(AllowedTilesVocabulary, self).__call__(context)

        if context is None:
            return vocabulary

        items = []
        for item in vocabulary:
            if checkPermission(item.value.add_permission, context):
                items.append(item)

        return SimpleVocabulary(items)
