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
        if not self.fieldname:
            info = IPrimaryFieldInfo(self.context, None)
            if info is None:
                # Ensure that we have at least a fieldname
                raise NotFound(self, '', self.request)
            self.fieldname = info.fieldname

            # respect field level security as defined in plone.autoform
            # check if attribute access would be allowed!
            try:
                guarded_getitem(self.context.data, self.fieldname)
            except KeyError:
                guarded_getattr(self.context, self.fieldname, None)

            file = info.value
        else:
            context = getattr(self.context, 'aq_explicit', self.context)
            try:
                file = guarded_getitem(context.data, self.fieldname)
            except KeyError:
                file = None
            if file is None:
                file = guarded_getattr(context, self.fieldname, None)

        if file is None:
            raise NotFound(self, self.fieldname, self.request)

        return file


class DisplayFile(NamedfileDisplayFile):
    """Display a file, via ../context/@@display-file/fieldname/filename

    Same as Download, however in this case we don't set the filename so the
    browser can decide to display the file instead.

    For tiles, this needs to combine our Download class above
    with the NamedfileDisplayFile class.
    """
    _getFile = Download._getFile
