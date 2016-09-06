# -*- coding: utf-8 -*-
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.supermodel import model
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserView


_ = MessageFactory('plone')


REGISTERED_TILES_VOCABULARY = 'plone.app.tiles.RegisteredTiles'
AVAILABLE_TILES_VOCABULARY = 'plone.app.tiles.AvailableTiles'
ALLOWED_TILES_VOCABULARY = 'plone.app.tiles.AllowedTiles'


class ITilesFormLayer(IPloneFormLayer):
    """Request layer installed via browserlayer.xml
    """


class ITileAddView(IBrowserView):
    """A tile add view as found by the @@add-tile traversal view.

    The default add view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """


class ITileEditView(IBrowserView):
    """A tile add view as found by the @@edit-tile traversal view.

    The default edit view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """


class ITileDeleteView(IBrowserView):
    """A tile delete view as found by the @@delete-tile traversal view.

    The default delete view is an adapter from (context, request, tile_info) to
    this interface. Per-tile type overrides can be created by registering
    named adapters matching the tile name.
    """


class ITileBaseSchema(model.Schema):
    """ Base interfaces from which all Plone tiles should inherit.
    """
