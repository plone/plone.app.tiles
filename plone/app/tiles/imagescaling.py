# -*- coding: utf-8 -*-
"""Image scale support for tile images."""
from Acquisition import aq_base
from DateTime import DateTime
from persistent.dict import PersistentDict
from plone.tiles.interfaces import IPersistentTile
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.interfaces import IStableImageScale
from plone.namedfile.scaling import ImageScale as BaseImageScale
from plone.namedfile.scaling import ImageScaling as BaseImageScaling
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.scale.storage import AnnotationStorage as BaseAnnotationStorage
from plone.scale.storage import IImageScaleStorage
from plone.tiles.interfaces import ITileDataManager
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
from zope.publisher.interfaces import NotFound


IMAGESCALES_KEY = "_plone.scales"


# For the storage, we adapt a context and an optional 'modified' callable.
@provider(IImageScaleStorage)
@adapter(IPersistentTile, Interface)
class AnnotationStorage(BaseAnnotationStorage):
    """An abstract storage for image scale data using annotations and
    implementing :class:`IImageScaleStorage`. Image data is stored as an
    annotation on the object container, i.e. the image. This is needed
    since not all images are themselves annotatable."""

    @property
    def storage(self):
        tile = self.context
        manager = ITileDataManager(tile)
        data = manager.get()
        if IMAGESCALES_KEY not in data:
            data[IMAGESCALES_KEY] = PersistentDict()
            manager.set(data)
        return data[IMAGESCALES_KEY]


class ImageScale(BaseImageScale):
    """view used for rendering image scales"""

    def __init__(self, context, request, **info):
        self.context = context
        self.request = request
        self.__dict__.update(**info)
        if self.data is None:
            try:
                self.data = getattr(self.context, self.fieldname)
            except AttributeError:
                self.data = self.context.data[self.fieldname]

        url = self.context.url
        extension = self.data.contentType.split("/")[-1].lower()
        if "uid" in info:
            name = info["uid"]
        else:
            name = info["fieldname"]
        self.__name__ = "%s.%s" % (name, extension)
        self.url = "%s/@@images/%s" % (url, self.__name__)
        self.srcset = info.get("srcset", [])

    def index_html(self):
        """download the image"""
        # validate access
        set_headers(self.data, self.request.response)
        return stream_data(self.data)


class ImageScaling(BaseImageScaling):
    """view used for generating (and storing) image scales"""

    _scale_view_class = ImageScale

    def get_field_data(self, name):
        try:
            return getattr(self.context, name)
        except AttributeError:
            return self.context.data[name]

    def publishTraverse(self, request, name):
        """used for traversal via publisher, i.e. when using as a url"""
        stack = request.get("TraversalRequestNameStack")
        image = None
        if stack and stack[-1] not in self._ignored_stacks:
            # field and scale name were given...
            scale = stack.pop()
            image = self.scale(name, scale)  # this is an aq-wrapped scale_view
            if image:
                return image
        elif "-" in name:
            # we got a uid...
            if "." in name:
                name, ext = name.rsplit(".", 1)
            storage = getMultiAdapter((self.context, None), IImageScaleStorage)
            info = storage.get(name)
            if info is None:
                raise NotFound(self, name, self.request)
            scale_view = self._scale_view_class(self.context, self.request, **info)
            alsoProvides(scale_view, IStableImageScale)
            return scale_view
        else:
            # otherwise `name` must refer to a field...
            if "." in name:
                name, ext = name.rsplit(".", 1)
            # This is the original code from plone.namedfile.
            # value = getattr(self.context, name)
            # This is now the only difference left that is needed for tiles.
            # TODO: we should make this customizable in plone.namedfile
            # with a new get_field_data method.
            value = self.get_field_data(name)
            scale_view = self._scale_view_class(
                self.context,
                self.request,
                data=value,
                fieldname=name,
            )
            return scale_view
        raise NotFound(self, name, self.request)

    def modified(self, fieldname=None):
        """provide a callable to return the modification time of content
        items, so stored image scales can be invalidated

        Note: the context (a tile) has no _p_mtime,
        so we need the _p_mtime of its context.
        """
        context = aq_base(self.context)
        if fieldname is not None:
            field = context.data.get(fieldname)
            field_p_mtime = getattr(field, "_p_mtime", None)
            date = DateTime(field_p_mtime or context.context._p_mtime)
            return date.millis()
        # We sum the modified time of various fields, which seems strange.
        # Maybe we should take the most recent one instead.
        # But it has been this way for a while, so let's keep it a bit longer.
        # Also, this part is not yet covered by the tests.
        mtime = 0
        for k, v in self.context.data.items():
            if INamedImage.providedBy(v):
                mtime += v._p_mtime
        if mtime:
            return mtime
        return DateTime(context.context._p_mtime).millis
