Changelog
=========

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
