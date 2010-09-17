import urllib

try:
    import json
except:
    import simplejson as json

from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.traversing.browser.interfaces import IAbsoluteURL

from plone.tiles.interfaces import ITileType, ITileDataManager, IPersistentTile

_safe = '@+'


def getEditTileURL(tile, request):
    """Get the edit URL for the given tile.

    If the tile is transient, the URL will contain a `_tiledata`
    parameter with the tile data encoded in JSON. This avoids possible
    collisions between raw data coming from the edit form and tile
    data retrieved by the transient tile data manager.
    """
    id = tile.id
    name = tile.__name__
    context = tile.__parent__

    if name is None or context is None:
        raise TypeError("Insufficient context to determine URL")

    url = str(getMultiAdapter((context, request), IAbsoluteURL))

    tileFragment = "@@edit-tile/" + urllib.quote(name.encode('utf-8'), _safe)
    if id:
        tileFragment += '/' + urllib.quote(id.encode('utf-8'), _safe)

    url = '%s/%s' % (url, tileFragment,)

    if not IPersistentTile.providedBy(tile):
        data = ITileDataManager(tile).get()
        if data:
            tileType = queryUtility(ITileType, name=name)
            if tileType is not None and tileType.schema is not None:
                if '?' in url:
                    url += '&' + '_tiledata=' + json.dumps(data)
                else:
                    url += '?' + '_tiledata=' + json.dumps(data)
    return url


def appendJSONData(url, key, data):
    """Append JSON data (e.g a dict) to the given URL and return the new
    URL. ``key`` is the url parameter key.
    """

    toAppend = "%s=%s" % (key, urllib.quote(json.dumps(data)),)

    if '?' in url:
        return url + '&' + toAppend
    else:
        return url + '?' + toAppend
