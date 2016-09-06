Plone's Specific Implementation of Tiles
========================================

.. image:: https://secure.travis-ci.org/plone/plone.app.tiles.png?branch=master
    :alt: Travis CI badge
    :target: http://travis-ci.org/plone/plone.app.tiles

.. image:: https://coveralls.io/repos/plone/plone.app.tiles/badge.png?branch=master
    :alt: Coveralls badge
    :target: https://coveralls.io/r/plone/plone.app.tiles

``plone.app.tiles`` is Plone's UI integration for `plone.tiles <http://pypi.python.org/pypi/plone.tiles>`_.

This package contains the following things:

* A view ``@@add-tile``, and an associated form, which can be used to create a new tile based on the tile's schema.
  For transient tiles, this merely redirects to a URL with an appropriate query string.
  For persistent tiles, it will also save the necessary data.
  This will fire an ``IObjectCreatedEvent`` as well as an ``IObjectAddedEvent`` for the newly created tile (a transient object) when successfully submitted.
  In the case of the ``IObjectAddedEvent``, the ``newParent`` attribute will be the tile's context, and the ``newName`` attribute will be the tile's id.

* The ``@@add-tile`` view, when accessed directly, allows the user to choose from all available tiles
  (subject to the tile's add permission)
  and redirects to the appropriate ``@@add-tile/<tile-type>`` URL to configure the tile.

* A view ``@@edit-tile``, and an associated form, which can be used to edit a tile based on the tile's schema.
  This will fire an ``IObjectModifiedEvent`` for the modified tile (a transient object) when successfully submitted.

* A view ``@@delete-tile``, and associated form, which can be used to delete a tile and associated persistent data.
  This can also be called by AJAX code given appropriate request parameters.
  This will fire an ``IObjectRemovedEvent`` for the removed tile (a transient object).
  The ``oldParent`` attribute will be the tile's context, and the ``oldName`` attribute will be the tile's id.

* A vocabulary ``plone.app.tiles.RegisteredTiles``, which contains all
  registered tile types.

* A vocabulary ``plone.app.tiles.AvailableTiles``, which contains all
  registered tile types, which have been registered for the current context.

* A vocabulary ``plone.app.tiles.AllowedTiles``, which contains all
  registered tile types, which have been registered for the current context,
  and, which are currently allowed to be added (for which the current
  user has required add permission).

The default add and edit forms should suffice for most use cases.
You can use `plone.autoform <http://pypi.python.org/pypi/plone.autoform>`_ to configure alternative widgets.

If you need a custom form,
you can register an add view as an adapter from ``(context, request, tileType)``,
where ``tileType`` is an instance providing ``plone.tiles.interfaces.ITileType``.

The actual integration of the various views is left up to other packages (such as the Mosaic editor).
