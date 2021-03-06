import math
import json
import re
import sys
import urllib
from itertools import repeat
from opener import Opener

def substr(string, start, length):
    return string[start:start+length]

def decodeLocation(loc):
    v10 = 0
    v2 = int(loc[0])
    v3 = loc[1:]
    v4 = int(math.floor((len(v3) / v2)))
    v5 = (len(v3) % v2)
    v6 = []
    v7 = 0
    while v7 < v5:
        v6.append(substr(v3,(v4 + 1)*v7,v4+1))
        v7 = v7 + 1
    v7 = v5
    while v7 < v2:
        v6.append(substr(v3, v4*(v7-v5)+(v4+1)*v5, v4))
        v7 = v7 + 1
    v8 = ""
    v7 = 0
    try:
        while v7 < len(v6[0]):
            v10 = 0
            while v10 < len(v6):
                v8 = v8 + v6[v10][v7]
                v10 = v10 + 1
            v7 = v7 + 1
    except:
        pass
    v8 = urllib.unquote(v8)
    v9 = ""
    v7 = 0
    while v7 < len(v8):
        if v8[v7] == "^":
            v9 = v9 + "0"
        else:
            v9 = v9 + v8[v7]
        v7 = v7 + 1
    v9 = v9.replace("+", " ")
    return v9

def xiami_get_single_song(song_id):
    url = xiami_url["single_song"] % song_id
    return xiami_zip(url)

def xiami_zip(url):
    loc, id, title, album, artist = \
    xiami_decode(url)
    return zip(loc, id, title,
               album, artist, repeat(False))

def xiami_get_album(album_id):
    url = xiami_url["album"] % album_id
    return xiami_zip(url)

def xiami_decode(url):
    content = Opener.Instance().open(url)
    encryptedLoc = getEncryptedLocation(content)
    titles = getTitle(content)
    ids = getId(content)
    albums = getAlbum(content)
    artists = getArtist(content)
    decodedLoc = [decodeLocation(loc) for loc in encryptedLoc]
    return decodedLoc, ids, titles, albums, artists

def getEncryptedLocation(content):
    return solveRegex(content, regexes["xiami_location"])

def getId(content):
    return solveRegex(content, regexes["xiami_id"])

def getAlbum(content):
    return solveRegex(content, regexes["xiami_album"])

def getArtist(content):
    return solveRegex(content, regexes["xiami_artist"])

def getTitle(content):
    return solveRegex(content, regexes["xiami_title"])

def solveRegex(content, pattern):
    v = re.findall(pattern, content, re.MULTILINE|re.DOTALL|re.U)
    return map(lambda x:x.decode("utf-8"), v)

regexes = {
    "xiami_id": r"\<song_id\>(.*?)\</song_id\>",
    "xiami_location": r"\<location\>(.*?)\</location\>",
    "xiami_title": r"<title><\!\[CDATA\[(.*?)\]\]></title>",
    "xiami_album": r"<album_name><\!\[CDATA\[(.*?)\]\]></album_name>",
    "xiami_artist": r"<artist><\!\[CDATA\[(.*?)\]\]></artist>",
    }

raw_patterns = [
    (r".*xiami.com/song/(?P<song_id>.*)", xiami_get_single_song),
    (r".*xiami.com/album/(?P<album_id>.*)", xiami_get_album)
    ]

patterns = map(lambda (reg, fn): (re.compile(reg), fn), raw_patterns)

xiami_url = {
    "single_song": "http://www.xiami.com/song/playlist/id/%s/object_name/default/object_id/0",
    "album": "http://www.xiami.com/song/playlist/id/%s/type/1",
    }

def dispatch_url(url):
    for (r, fn) in patterns:
        m = r.match(url)
        if m:
            return fn(m.group(1))
    raise Exception("unmatchable url")

if __name__ == "__main__":
    url = sys.argv[1]
    result = dispatch_url(url)
    print result
