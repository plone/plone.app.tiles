# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = "4.0.0"
long_description = (
    open("README.rst").read()
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
)

setup(
    name="plone.app.tiles",
    version=version,
    description="Plone UI integration for plone.tiles",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone tiles deco",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://github.com/plone/plone.app.tiles",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        "six",
        "zope.annotation",
        "zope.i18nmessageid",
        "plone.namedfile >= 6.0.0a3",
        "plone.memoize",
        "plone.registry",
        "plone.tiles",
        "zope.publisher",
        "zope.security",
        "zope.component",
        "zope.interface",
        "plone.z3cform",
        "plone.autoform",
        "z3c.form",
        "plone.uuid",
        "Products.statusmessages",
        "zope.traversing",
        "zope.event",
        "zope.lifecycleevent",
        "zope.schema",
        "Zope",
        "AccessControl",
    ],
    extras_require={
        "test": [
            "Pillow",
            "plone.app.drafts",
            "plone.app.relationfield",
            "plone.app.testing",
            "plone.dexterity",
            "plone.app.dexterity",
        ],
    },
)
