from flask import Flask, Response, jsonify, url_for, abort
import urllib,re, sys, os, requests, json
from functools import wraps
import urllib.request as urllib2
import ssl 
try:
    _create_unverified_https_context = ssl._create_unverified_context 

except AttributeError: 
    pass 
else: 
    ssl._create_default_https_context =_create_unverified_https_context

MANIFEST = {
    'id': 'vijai',
    'version': '1.0.2',
    'name': 'vijai',
    'description': 'Sample addon made with Flask providing a few public domain movies',
    'types': ['movie'],
    'catalogs': [{'type': 'movie','name':'tamilgun_HD_movies','id': 'tamilgun_HD_movies'},{'type': 'movie','name':'tamilgun_New_movies','id': 'tamilgun_New_movies'}],
 	'resources': [
        'catalog',
        'stream',
        'meta'

        # The meta call will be invoked only for series with ID starting with hpy
        #{'name': "meta", 'types': ["movie"], 'idPrefixes': ["tamilgun_HD_movies","tamilgun_New_movies"]},
        #{'name': 'stream', 'types': ["movie"], 'idPrefixes': ["tamilgun_HD_movies","tamilgun_New_movies"]}
    ],

}

# STREAMS = {
#     'movie': {
#         'tt0032138': [
#             {'title': 'Torrent',
#                 'infoHash': '24c8802e2624e17d46cd555f364debd949f2c81e', 'fileIdx': 0}
#         ],
#         'tt0017136': [
#             {'title': 'Torrent',
#                 'infoHash': 'dca926c0328bb54d209d82dc8a2f391617b47d7a', 'fileIdx': 1}
#         ],
#         'tt0051744': [
#             {'title': 'Torrent', 'infoHash': '9f86563ce2ed86bbfedd5d3e9f4e55aedd660960'}
#         ],
#         'tt1254207': [
#             {'title': 'HTTP URL', 'url': 'https://www94.playercdn.net/86/3/ohbiiF9Y2a9zYpAf7TEtPg/1565239650/190806/472G5Q4NLQ7Y5XLKRGGM2.mp4'}
#         ],
#         'tt0031051': [
#             {'title': 'YouTube', 'ytId': 'm3BKVSpP80s'}
#         ],
#         'tt0137523': [
#             {'title': 'External URL',
#                 'externalUrl': 'https://www.netflix.com/watch/26004747'}
#         ]
#     }
# }
# CATALOG = {
#     'movie': [
#         {'id': 'tt0032138', 'name': 'The Wizard of Oz', 'genres': [
#             'Adventure', 'Family', 'Fantasy', 'Musical']},
#         {'id': 'tt0017136', 'name': 'Metropolis',
#          'genres': ['Drama', 'Sci-Fi']},
#         {'id': 'tt0051744', 'name': 'House on Haunted Hill',
#          'genres': ['Horror', 'Mystery']},
#         {'id': 'tt1254207', 'name': 'Big Buck Bunny',
#          'genres': ['Animation', 'Short', 'Comedy'], },
#         {'id': 'tt0031051', 'name': 'The Arizona Kid',
#          'genres': ['Music', 'War', 'Western']},
#         {'id': 'tt0137523', 'name': 'Fight Club', 'genres': ['Drama']}
#     ]
#     }
#METAHUB_URL = 'https://images.metahub.space/poster/medium/{}/img'
def getdatacontent(url,reg):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    req = urllib2.Request(url)
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    r = opener.open(req)
    html = r.read().decode('utf-8')
    data = re.compile(reg).findall(html)
    return data

def gethtmlcontent(url):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    req = urllib2.Request(url)
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    r = opener.open(req)
    html = r.read().decode('utf-8')
    return html

def getstreamurl(url):
    reg = "<a onclick=\"window.open\('(.*?)'"
    iframe = getdatacontent(url,reg)
    if iframe:
            for url in iframe:
                if "embed1.tamildbox" in url:
                    if "https" in url:
                        url = url 
                    elif "http" in url:
                        url = url.replace("http","https")
                    else:
                        url = 'https:'+url
                html1 = gethtmlcontent(url)
                movieurl= re.compile("domainStream = '(.*?)'").findall(html1)
                if movieurl:
                    return movieurl
                elif "domainStream = domainStream.replace('hls_vast', 'hls')" in html1:
                	url = url.replace('hls_vast', 'hls')
                	url = url.replace('.tamildbox.tips', '.tamilgun.tv')
                	url = url + '/playlist.m3u8'
                	movieurl = url
                	return movieurl
                else:
                	movieurl = ""
                	return movieurl


def appenddatatocatalog(data,id):
    CATALOG[id] = {}
    CATALOG[id]['movie'] = []
    for item in data:
        temp = {}
        temp['poster'] = item[0]
        temp['name'] = item[1] 
        temp['id'] = id+'_-'+item[1]
        CATALOG[id]['movie'].append(temp)
        url = item[2]
        stream_url = getstreamurl(url)
        stream_temp={}
        stream_temp['title'] = 'HTTP URL'
        if stream_url:
        	if isinstance(stream_url,list):
        		stream_temp['url'] = stream_url[0]
        	if isinstance(stream_url,str):
        		stream_temp['url'] = stream_url
        else:
            stream_temp['url'] = ''
        STREAMS['movie'].update({temp['id']:[stream_temp]})





#### Main Program Starts Here #############
global STREAMS
global CATALOG
CATALOG = {}
STREAMS = {}
STREAMS['movie'] = {}
url = "http://tamilgun.com"
r = requests.get(url) 
url = r.url
url = url.split("/")
url = "http://"+url[2]
tamilgun_HD_movie = url+"/categories/hd-movies/"
reg = "<img src=\" (.*?) \" alt=\"(.*?)\" \/>\s+<div class=\"rocky-effect\">\s+<a href=\"(.*?)\" >"
data = getdatacontent(tamilgun_HD_movie,reg)
appenddatatocatalog(data,"tamilgun_HD_movies")
tamilgun_New_movie = url+"/categories/new-movies-a/"
reg = "<img src=\" (.*?) \" alt=\"(.*?)\" \/>\s+<div class=\"rocky-effect\">\s+<a href=\"(.*?)\" >"
data = getdatacontent(tamilgun_New_movie,reg)
appenddatatocatalog(data,"tamilgun_New_movies")

app = Flask(__name__)

def respond_with(data):
    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp


@app.route('/manifest.json')
def addon_manifest():
    return respond_with(MANIFEST)

@app.route('/stream/<type>/<id>.json')
def addon_stream(type,id):
    if type not in MANIFEST['types']:
        abort(404)

    streams = {'streams': []}
    if type in STREAMS and id in STREAMS[type]:
        streams['streams'] = STREAMS[type][id]
    return respond_with(streams)

@app.route('/catalog/<type>/<id>.json')
def addon_catalog(type, id):
    if type not in MANIFEST['types']:
        abort(404)

    catalog = CATALOG[id][type] if type in CATALOG[id] else []
    metaPreviews = {
        'metas': [
            {
                'id': item['id'],
                'type': type,
                'name': item['name'],
                'poster': item['poster'],
                'director': 'vijai',
                'background': item['poster']
            } for item in catalog
        ]
    }
    return respond_with(metaPreviews)

OPTIONAL_META = ["posterShape", "background", "logo", "videos", "description", "releaseInfo", "imdbRating", "director", "cast",
                 "dvdRelease", "released", "inTheaters", "certification", "runtime", "language", "country", "awards", "website", "isPeered"]


@app.route('/meta/<type>/<id>.json')
def addon_meta(type,id):
    if type not in MANIFEST['types']:
        abort(404)

    def mk_item(item):
        meta = dict((key, item[key])
                    for key in item.keys() if key in OPTIONAL_META)
        meta['id'] = item['id']
        meta['type'] = type
        meta['name'] = item['name']
        meta['poster'] = item['poster']
        meta['director'] = 'vijai'
        meta['background'] = item['poster']
        return meta
    name = id.split('_-')
    name = name[0]
    meta = {
        'meta': next((mk_item(item)
                      for item in CATALOG[name][type] if item['id'] == id),
                     None)
    }

    return respond_with(meta)


if __name__ == '__main__':
    app.run()
