from setuptools import setup, find_packages
import os

version = '1.0a1'
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='plone.app.tiles',
      version=version,
      description="Plone UI integration for plone.tiles",
      long_description=long_description,
      classifiers=[
        "Development Status :: 3 Alpha",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
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
          'plone.app.drafts',
          'plone.autoform',
          'plone.memoize',
          'plone.uuid',
          'z3c.form',
          'zope.traversing',
          'zope.lifecycleevent >= 3.5.2',
          'zope.event',
          'zope.component',
          'zope.event',
          'zope.security',
          'Zope2',
      ],
      extras_require={
        'test': ['plone.app.testing'],
      },
      entry_points="""
      """,
      )
