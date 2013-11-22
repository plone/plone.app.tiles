from setuptools import setup, find_packages
import sys

version = '1.0.1'

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    requires = ['simplejson']
else:
    requires = []

tests_require = ['plone.app.testing']

long_description = \
    open("README.rst").read() + \
    "\n" + \
    open("./CREDITS.rst").read() + \
    "\n" + \
    open("CHANGELOG.rst").read()

setup(
    name='plone.app.tiles',
    version=version,
    description="Plone UI integration for plone.tiles",
    long_description=long_description,
    classifiers=[
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
    url='https://github.com/plone/plone.app.tiles',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.annotation',
        'zope.i18nmessageid',
        'plone.namedfile',
        'plone.memoize',
        'plone.registry',
        'plone.tiles',
        'zope.publisher',
        'zope.security',
        'zope.component',
        'zope.interface',
        'plone.app.blocks',
        'plone.app.drafts',
        'plone.z3cform',
        'plone.autoform',
        'z3c.form',
        'plone.uuid',
        'Products.statusmessages',
        'zope.traversing',
        'zope.event',
        'zope.lifecycleevent',
        'zope.schema',
        'Zope2',
        'AccessControl',
    ] + requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
    """,
)
