from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.app.tiles',
      version=version,
      description="Plone UI integration for plone.tiles",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone tiles deco',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/plone.app.tiles',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.tiles',
          'plone.autoform',
          'plone.memoize',
          'z3c.form',
          'zope.traversing',
          'zope.lifecycleevent',
          'zope.event',
          'zope.component',
          'zope.event',
          'zope.security',
          'Zope2',
      ],
      extras_require={
        'test': ['collective.testcaselayer', 'Products.PloneTestCase'],
      },
      entry_points="""
      """,
      )
