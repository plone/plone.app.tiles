# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone.namedfile.browser import Download as NamedfileDownload
from plone.namedfile.browser import DisplayFile as NamedfileDisplayFile
from AccessControl.ZopeGuards import guarded_getattr
from AccessControl.ZopeGuards import guarded_getitem
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from ZPublisher.HTTPRangeSupport import expandRanges
from ZPublisher.HTTPRangeSupport import parseRange

import os



def _shared_getFile(tile_view):
    """Get a file from a tile.

    This is used by both Download and DisplayFile.
    I had this as method on the Download class,
    and then defined DisplayFile like this:

        class DisplayFile(NamedfileDisplayFile):
            _getFile = Download._getFile

    This works on Python 3, but on Python 2 you get this error:

        TypeError: unbound method _getFile() must be called with Download
        instance as first argument (got nothing instead)

    I did not want to bother with multiple inheritance,
    so I made this a function that both classes call.
    """
    if not tile_view.fieldname:
        info = IPrimaryFieldInfo(tile_view.context, None)
        if info is None:
            # Ensure that we have at least a fieldname
            raise NotFound(tile_view, '', tile_view.request)
        tile_view.fieldname = info.fieldname

        # respect field level security as defined in plone.autoform
        # check if attribute access would be allowed!
        try:
            guarded_getitem(tile_view.context.data, tile_view.fieldname)
        except KeyError:
            guarded_getattr(tile_view.context, tile_view.fieldname, None)

        file = info.value
    else:
        context = getattr(tile_view.context, 'aq_explicit', tile_view.context)
        try:
            file = guarded_getitem(context.data, tile_view.fieldname)
        except KeyError:
            file = None
        if file is None:
            file = guarded_getattr(context, tile_view.fieldname, None)

    if file is None:
        raise NotFound(tile_view, tile_view.fieldname, tile_view.request)

    return file



@implementer(IPublishTraverse)
class Download(NamedfileDownload):
    """Download a file, via ../context/@@download/fieldname/filename

    `fieldname` is the name of an attribute on the context that contains
    the file. `filename` is the filename that the browser will be told to
    give the file. If not given, it will be looked up from the field.

    The attribute under `fieldname` should contain a named (blob) file/image
    instance from this package.

    If no `fieldname` is supplied, then a default field is looked up through
    adaption to `plone.rfc822.interfaces.IPrimaryFieldInfo`.
    """

    def _getFile(self):
        return _shared_getFile(self)


class DisplayFile(NamedfileDisplayFile):
    """Display a file, via ../context/@@display-file/fieldname/filename

    Same as Download, however in this case we don't set the filename so the
    browser can decide to display the file instead.

    For tiles, this needs to combine our Download class above
    with the NamedfileDisplayFile class.
    """

    def _getFile(self):
        return _shared_getFile(self)
