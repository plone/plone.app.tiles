# -*- coding: utf-8 -*-

from plone.app.tiles import modifiers
from Products.CMFCore.utils import getToolByName


def install_modifiers(context):
    try:
        portal = context.getSite()
    except AttributeError:
        portal = context.portal_url.getPortalObject()
    portal_modifier = getToolByName(portal, 'portal_modifier')
    modifiers.install(portal_modifier)


def post_setup(context):
    if context.readDataFile('plone.app.tiles_default.txt') is None:
        return
    install_modifiers(context)
