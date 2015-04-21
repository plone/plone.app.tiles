# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.0.0'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(
    name='plone.app.tiles',
    version=version,
    description="Plone UI integration for plone.tiles",
    long_description=long_description,
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='plone tiles deco',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/plone/plone.app.tiles',
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
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.drafts',
        ],
    },
)
