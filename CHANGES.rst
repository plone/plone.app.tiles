Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

4.0.2 (2025-06-19)
------------------

Bug fixes:


- Fix calculation of canonical header in namedfile views. @petschki


Internal:


- Configure package with plone/meta
  [petschki] (#0)
- Remove deprecated plone.app.tiles registry record from the demo profile.
  [thet]
- Update configuration files.
  [plone devs]


4.0.1 (2023-12-14)
------------------

- Use ``ScalesDict`` instead of ``PersistentDict`` to store scales in persistent tiles.
  This avoids ``plone.protect`` warning about write-on-read.
  Migrate the storage on-the-fly, just like ``plone.scale`` does.
  [maurits]


4.0.0 (2022-12-02)
------------------

- Add support for Plone 6 on Python 3.10 and 3.11.  [maurits]


4.0.0a2 (2022-07-20)
--------------------

- Register our demo tiles when you explicitly load ``demo.zcml``.
  Add them to the list in ``plone.app.tiles`` and ``plone.app.mosaic``.
  [maurits]

- Accept a fieldname in ``get_original_value`` in our scaling code.
  Needed for recent plone.namedfile versions.
  [maurits]


4.0.0a1 (2022-03-09)
--------------------

- Register our own ``IImageScaleFactory`` factory for persistent tiles.
  This fixes scaling images on tiles when the tile does not have the workaround of defining a property for the image field.
  [maurits]

- Register our ``AnnotationStorage`` as ``IImageScaleStorage`` factory.
  We require ``plone.namedfile >= 6.0.0a2`` for this.
  Fixes `issue 48 <https://github.com/plone/plone.app.tiles/issues/48>`_.  [maurits]

- Drop support for Python 2 and Plone 5.1.
  Plone 5.2 and 6.0 are supported, on Python 3.
  See `issue 49 <https://github.com/plone/plone.app.tiles/issues/49>`_.  [maurits]


3.3.0 (2022-02-04)
------------------

Features:

- Define ``download`` and ``display-file`` views that work for tiles.
  The original views in ``plone.namedfile`` cannot find the tile data.
  [maurits]

Bug fixes:

- Fixed getting original image from tile.
  Until now, the ``images`` view tried to get the field from the tile instead of the tile data.
  This only worked when you had explicitly added a property with this field name on the tile.
  [maurits]


3.2.3 (2022-01-28)
------------------

- Removed ``plone.namedfile[blobs]`` from the ``test`` extra.
  This has been empty since ``plone.namedfile`` 2.0, used since Plone 4.3.0.
  [maurits]


3.2.2 (2021-12-21)
------------------

Features:

- test with github actions
  [petschki]

Bug fixes:

- Fix imagescaling: missing srcset initialization, and
  wrong scale arguments (according to latest p.namedfile).
  Add test for imagescaling.
  [mamico]

- Fix class security declaration warnings for add/edit/delete views
  [petschki]


3.2.1 (2020-09-26)
------------------

- Fix ModuleNotFoundError: No module named 'App.class_init' on Zope 5.
  [agitator]


3.2.0 (2020-08-21)
------------------

New features:

- Officially dropped support for Plone 5.0.
  No related changes, but we will no longer test with it.
  [maurits]

Bug fixes:

- Fix losing an image on edit when it is not changed.
  Fixes `issue 36 <https://github.com/plone/plone.app.tiles/issues/36>`_.
  [lyralemos, maurits]

- Updated Travis test setup.
  Test with Plone 4.3, 5.1, 5.2.  Last one on Py 2.7, 3.6. 3.7, 3.8.
  [maurits]


3.1.3 (2020-03-21)
------------------

Bug fixes:

- Update trove classifiers
  [petschki]


3.1.2 (2019-04-18)
------------------

Bug fixes:

- Python 3 compatible urllib imports
  [petschki]

- Fix imagescaling methods, by removing calls of no longer existing __of__ method
  [MrTango]


3.1.1 (2019-02-10)
------------------

- Python 3 compatibility
  [vangheem, petschki]


3.1.0 (2018-07-05)
------------------

- Add to pass extra parameters given for add-tile-traverser forward to tile add
  form
  [datakurre]

- Fieldset support in tile schemas
  [datakurre]


3.0.3 (2017-01-02)
------------------

Bug fixes:

- Fix issue where tile image scaling leaked didn't close opened files
  [datakurre]


3.0.2 (2016-12-21)
------------------

Bug fixes:

- Fix issue where deprecated fieldname was passed to getAvailableSizes
  [datakurre]


3.0.1 (2016-11-24)
------------------

Bug fixes:

- ``plone_view/mark_view`` was deprecated and removed in Plone 5.1.
  Use ``plone_layout/mark_view`` instead.
  [thet]


3.0.0 (2016-09-15)
------------------

Breaking changes:

- Remove ``Add tile`` (plone.app.tiles.AddTile) permission, because
  it was not use by default and each tiles may have its own add permission
  and use existing permissions like ``cmf.ModifyPortalContent``.
  [datakurre]

- Deprecate registry record ``plone.app.tiles``. The registry
  record is still registered, but not used by plone.app.tiles
  [datakurre]

New features:

- Add CMFEditions modifier to prevent (previously broken) versioning of blobs
  and relations in persistent tile data (in annotations); Whenever a previous
  version is restored, the blob and relation versions from the current
  working copy version are applied for the restored version
  [datakurre]

- Add new vocabularies *plone.app.tiles.RegisteredTiles*,
  *plone.app.tiles.AvailableTiles* and *plone.app.tiles.AllowedTiles* to
  list all registered tiles, tiles available in the current context
  and tiles allowed to be added in the current context by the current user
  [datakurre]

- Add support for drafting preview when request has
  plone.app.drafts.interfaces.IDisplayFormDrafting
  (requires plone.app.drafts >= 1.1.0)
  [datakurre]

Bug fixes:

- Fix to use z3c.form's applyForm() in tile add and edit forms so
  IDataManagers get used and complex fields are filled properly
  [danmur]

Refactoring:

- Use @property instead of property().
  [gforcada]

- Reformat docs and update some references.
  [gforcada]

- Update testing infrastructure.
  [gforcada]

2.2.1 (2016-04-06)
------------------

- Fix default role assignment: Remove Reviewer and add Contributor to
  'Add Tile' permission in ``rolemap.xml``.
  [jensens]

2.2.0 (2015-09-04)
------------------

- Remove unnecessary dependency on plone.app.blocks
  [datakurre]

- Fix issue where expected all drafted tiles to be mentioned in very specific
  layout field; Fixed to sync all drafted tiles instead
  [datakurre]

2.1.0 (2015-05-25)
------------------

- Remove deprecated support for @@delete-tile/tile-id and refactor view at
  @@delete-tile/tile-name/tile-id into a form to support automatic CSRF
  protection in Plone 5
  [datakurre]
- Remove status messages from tile form operations
  [datakurre]
- Remove tiledata JavaScript-variable from tile form templates
  [datakurre]
- Change imagescaling data for persistent tiles to be saved into tile data
  instead of a separate annotation
  [datakurre]
- Fix issue where tile preview during drafting did not use drafting tile data
  for the preview
  [datakurre]
- Fix issue where catalog source could not properly check permissions on tile
  edit form with wrapping edit form tile data into acquisition wrapper
  [datakurre]
- Fix tile form action URLs to contain transient tile state
  [datakurre]
- Move tile form action info JSON in form action redirect URLs from query to
  fragment
  [datakurre]

2.0.0 (2015-04-21)
------------------

- Remove base tag, which is removed in Plone 5
  [robgietema]
- Change tile delete API to match add and edit APIs
  [simahawk]
- Change add traversal tile type parameter from tiletype to justa type
  [bloodbare]
- Add Italian translation
  [gborelli]
- Add nextURL as function for AddForm and DefaultEditForm
  for better overriding support
  [datakurre]
- Add to send out events after status message created
  [vangheem]
- Add imagescaling
  [ableeb, simahawk]
- Add tile editing to trigger object modified event
  [ableeb]
- Add AddTile-permission
  [tisto]
- Add support for deferred security checking for traversal (fixes #3)
  [cewing]
- Add tile wrapper template for reusable common tile structure
  [garbas]
- Fix to not crash when plone.app.tiles-registry contains missing tiles
  [datakurre]
- Fix issue with wrong doctype for responses with inline javascript
  [jpgimenez]
- Fix issues with changed plone overlay API
  [garbas]
- PEP8, coverage, packaging and test fixes
  [garbas, gforcada, hvelarde, jfroche, tisto]
- Remove custom classes (klass) option from tile base schema
  [vangheem]

1.0.1 (2012-06-25)
------------------

- fixing 1.0 release which was broken (missing README.rst)
  [garbas]

1.0 (2012-06-23)
----------------

- initial release.
  [garbas]
