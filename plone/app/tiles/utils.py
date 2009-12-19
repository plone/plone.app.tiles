import urllib

try:
    import json
except:
    import simplejson as json

def getEditTileURL(tileURL):
    """Given a tile URL, return the corresponding edit tile URL
    """
    
    urlParts = tileURL.split('/')
    urlParts.insert(-2, '@@edit-tile')
    if urlParts[-2].startswith('@@'):
        urlParts[-2] = urlParts[-2][2:]
    
    return '/'.join(urlParts)

def appendJSONData(url, key, data):
    """Append JSON data (e.g a dict) to the given URL and return the new
    URL. ``key`` is the url parameter key.
    """
    
    toAppend = "%s=%s" % (key, urllib.quote(json.dumps(data)),)
    
    if '?' in url:
        return url + '&' + toAppend
    else:
        return url + '?' + toAppend
