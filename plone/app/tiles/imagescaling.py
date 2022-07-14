# -*- coding: utf-8 -*-
"""Image scale support for tile images."""
from AccessControl.ZopeGuards import guarded_getattr
from Acquisition import aq_base
from DateTime import DateTime
from persistent.dict import PersistentDict
from plone.tiles.interfaces import IPersistentTile
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.scaling import ImageScale as BaseImageScale
from plone.namedfile.scaling import ImageScaling as BaseImageScaling
from plone.namedfile.scaling import DefaultImageScalingFactory
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.scale.storage import AnnotationStorage as BaseAnnotationStorage
from plone.scale.storage import IImageScaleStorage
from plone.scale.interfaces import IImageScaleFactory
from plone.tiles.interfaces import ITileDataManager
from zExceptions import Unauthorized
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider


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


@implementer(IImageScaleFactory)
@adapter(IPersistentTile)
class TileImageScalingFactory(DefaultImageScalingFactory):
    def get_original_value(self, fieldname=None):
        fieldname = fieldname or self.fieldname
        if fieldname is not None:
            return self.context.data.get(fieldname)

    def url(self):
        return "{}/@@{}/{}".format(
            self.context.context.absolute_url(),
            self.context.__name__,
            self.context.id,
        )


class ImageScaling(BaseImageScaling):
    """view used for generating (and storing) image scales"""

    _scale_view_class = ImageScale

    def guarded_orig_image(self, fieldname):
        # First try attribute access: the tile may have a property for the image,
        # and this may be better protected than the tile data, which is a simple dict.
        try:
            return guarded_getattr(self.context, fieldname)
        except Unauthorized:
            # There is an image (or other field), but the user has no access.
            return None
        except AttributeError:
            # Return the image from the tile data.
            return self.context.data[fieldname]

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
