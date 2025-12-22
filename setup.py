from setuptools import setup


version = "5.0.0.dev0"
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
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone tiles deco",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://github.com/plone/plone.app.tiles",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        "zope.annotation",
        "zope.i18nmessageid",
        "plone.namedfile >= 6.0.0a3",
        "plone.memoize",
        "plone.registry",
        "plone.scale >= 4.0.1",
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
