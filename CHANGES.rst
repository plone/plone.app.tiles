Changelog
=========

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
- Fix issue with wrong doctype for reponses with inline javascript
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
