from plone import tiles
from plone.namedfile.field import NamedImage
from plone.supermodel.model import fieldset
from zope import schema
from zope.interface import Interface


class ITransientTileData(Interface):

    message = schema.TextLine(title="Test string")


class TransientTile(tiles.Tile):
    def __call__(self):
        return (
            "<html><body><b>Transient tile %s</b></body></html>" % self.data["message"]
        )


class IPersistentTileData(Interface):

    message = schema.TextLine(title="Persisted message")
    counter = schema.Int(title="Counter")
    image = NamedImage(title="Image", required=False)
    image2 = NamedImage(title="Image2", required=False)

    fieldset("counter", label="Counter", fields=["counter"])


class PersistentTile(tiles.PersistentTile):
    __name__ = "plone.app.tiles.demo.persistent"

    def Title(self):
        return self.data["message"]

    @property
    def image(self):
        # Explicitly define an image property to ease getting the original.
        # Note that we only do this for the first image, not the second,
        # so we can try out multiple ways of getting an image.
        return self.data["image"]

    def __call__(self):
        return "<html><body><b>Persistent tile {} #{}</b></body></html>".format(
            self.data["message"],
            self.data["counter"],
        )
