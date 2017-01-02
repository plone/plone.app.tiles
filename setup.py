# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '3.0.3'
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
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
            'Pillow',
            'plone.app.drafts',
            'plone.app.relationfield',
            'plone.app.testing',
            'plone.dexterity',
            'plone.app.dexterity',
            'plone.namedfile[blobs]',
        ],
    },
)
