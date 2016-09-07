# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import ManagePortal

_ = MessageFactory('plone')


def initialize(context):
    """Registers modifiers with zope (on zope startup).
    """
    from plone.app.tiles.modifiers import modifiers

    for modifier in modifiers:
        context.registerClass(
            modifier['wrapper'], modifier['id'],
            permission=ManagePortal,
            constructors=(modifier['form'], modifier['factory']),
            icon=modifier['icon'],
        )
