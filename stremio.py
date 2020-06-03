from flask import Flask, Response, jsonify, url_for, abort
import urllib,re, sys, os, requests, json
from functools import wraps
import urllib.request as urllib2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
    'catalogs': [{'type': 'movie','name':'tamilgun_HD_movies','id': 'tamilgun_HD_movies'},{'type': 'movie','name':'tamilgun_New_movies','id': 'tamilgun_New_movies'},{'type': 'movie','name':'movierulz_tamil','id': 'movierulz_tamil'}],
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
    data = []
    try:
        r = opener.open(req)
        html = r.read().decode('utf-8')
        data = re.compile(reg).findall(html)
        print (data)
        return data
    except:
        print ("Error getting data content---------------*-*-*-*-")

# def gethtmlcontent(url):
#     try:
#         _create_unverified_https_context = ssl._create_unverified_context 

#     except AttributeError: 
#         pass 
#     else: 
#         ssl._create_default_https_context =_create_unverified_https_context
#     proxy_handler = urllib2.ProxyHandler({})
#     opener = urllib2.build_opener(proxy_handler)
#     req = urllib2.Request(url)
#     opener.addheaders = [('User-agent', 'Mozilla/5.0')]
#     r = opener.open(req)
#     html = r.read().decode('utf-8')
#     return html

def gethtmlcontent(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"}
    response = requests.get(url, headers=headers, verify=False)
    result = response.text
    return result

def gettamilgunstreamurl(url):
    movielist = []
    temp = {}
    temp['title'] = "embed1.tamildbox"
    html = gethtmlcontent(url)
    reg = "<a onclick=\"window.open\('(.*?)'"
    iframe= re.compile("<a onclick=\"window.open\('(.*?)'").findall(html)
    if iframe:
            for url in iframe:
                if "embed1.tamildbox" in url:
                    if "https" in url:
                        url = url
                    elif "http" in url:
                        url = url.replace("http","https")
                    else:
                        url = 'https:'+url
                try:
                    html1 = gethtmlcontent(url)
                    movieurl= re.compile("domainStream = '(.*?)'").findall(html1)
                    if movieurl:
                        movieurl = movieurl[0]
                        html2 = gethtmlcontent(movieurl)
                        urllastpart= html2.split('\n')
                        urllastpart = urllastpart[-2]
                        movieurl = movieurl.replace('playlist.m3u8',urllastpart)
                        #movieurl = movieurl[0].replace('https','http')
                        temp['url'] = movieurl
                        movielist.append(temp)
                    elif "domainStream = domainStream.replace('hls_vast', 'hls')" in html1:
                        url = url.replace('hls_vast', 'hls')
                        url = url.replace('.tamildbox.tips', '.tamilgun.tv')
                        url = url + '/playlist.m3u8'
                        movieurl = url
                        if "https" in movieurl:
                            movieurl = movieurl.replace('https','http')
                        temp['url'] = movieurl
                        movielist.append(temp)
                except:
                    temp['url'] = ""
                    movielist.append(temp)
                    print("Error getting datacontent")
    temp = {}
    iframe= re.compile('sources:\s+\[{\"file\":\"(.*?)\"}\]').findall(html)
    if iframe:
        for url in iframe:
            if "vidorg.net" in url:
                temp['title'] = "vidorg.net"
                url = url.replace('\/','/')
                url = url.split(',')
                url = url[0]+url[3]+'/index-v1-a1.m3u8'
                temp['url'] = url
                movielist.append(temp)
    temp = {}
    iframe= re.compile('<IFRAME SRC=\"(.*?)\"').findall(html)
    if iframe:
        for url in iframe:
            if "chromecast.video" in url:
                temp['title'] = "chromecast.video"
                if "https" in url:
                    url = url 
                elif "http" in url:
                    url = url.replace("http","https")
                else:
                    url = 'https:'+url
                
                headers = {
                    'Connection': 'keep-alive',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                    'Sec-Fetch-User': '?1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,ta-IN;q=0.8,ta;q=0.7,fr-FR;q=0.6,fr;q=0.5',
                }

                response = requests.get(url, headers=headers)
                html1 = response.text
                movieurl = re.compile('sources:\s+\[\"(.*?)\",\"(.*?)\"\]').findall(html1)
                movieurl = movieurl[0]
                
                if movieurl[0]:
                    headers = {
                        'Connection': 'keep-alive',
                        'Origin': 'https://chromecast.video',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                        'DNT': '1',
                        'Accept': '*/*',
                        'Sec-Fetch-Site': 'same-site',
                        'Sec-Fetch-Mode': 'cors',
                        'Referer': url,
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.9,ta-IN;q=0.8,ta;q=0.7,fr-FR;q=0.6,fr;q=0.5',
                    }
                    response = requests.get(movieurl[0], headers=headers)
                    html1 = response.text
                    movieurl = re.compile('https:\/\/(.*?)index-v1-a1.m3u8').findall(html1)
                    if movieurl[-1]:
                        movieurl = 'https://'+movieurl[-1]+'index-v1-a1.m3u8'
                        temp['url'] = movieurl
                        movielist.append(temp)

    print('start----------------------------------------------------------')
    print(movielist)
    print('end -----------------------------------------------------------')
    return movielist

def getmovierulzstreamurl(url):
    movielist = []
    temp = {}
    html = gethtmlcontent(url)
    data= re.compile('<p><strong>(.*?)<\/strong><br \/>\s+<a href=\"(.*?)\"').findall(html)
    for item in data:
        if ("Openload" in item[0]):
            try:
                url = getdatacontent(item[1],"(?:iframe src|IFRAME SRC)=\"(.+?)\"")
                movieurl = url[0]
                if movieurl:
                    temp['title'] = "openload"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch openload URL")      
        if ("Streamango" in item[0]):
            movieurl = item[1]
            if movieurl:
                temp['title'] = "Streamango"
                temp['url'] = movieurl
                movielist.append(temp)
                temp = {}
        if ("Netutv" in item[0]):
            print("work in progress")
        if ("Oneload" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    temp['title'] = "oneload"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL") 
        if ("estream" in item[1]):
            try:
                movieurl = item[1]
                if movieurl:
                    temp['title'] = "estream"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL") 
        if ("Prostream" in item[0]):
            print("work in progress")
        if ("Oload" in item[0]):
            print("work in progress")
        if ("Vidzi" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    temp['title'] = "vidzi"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL")
        if ("vidoza" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    tempurl = getdatacontent(movieurl, 'sourcesCode: \[{ src: \"(.*?)\", type: "video\/mp4", label:\"(.*?)\", res:\"(.*?)\"}\]')
                    tempurl = tempurl[0]
                    print("fetching vidoza URL") 
                    print(tempurl[0])
                    tempurl = tempurl[0].replace('https','http')
                    print(tempurl)
                    temp['title'] = "vidoza"
                    temp['url'] = tempurl
                    movielist.append(temp)
                    temp = {} 
                    #addDir('folder','playurl',tempurl[0],"vidoza",getImgPath("openload_icon"),getImgPath("openload_fanart"))
            except:
                print("unable to fetch Oneload URL") 
        if ("vup" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    temp['title'] = "vup"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL")
        if ("netutv" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    temp['title'] = "netutv"
                    temp['url'] = movieurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL")
        if ("videobin" in item[0]):
            try:
                movieurl = item[1]
                if movieurl:
                    print("entering videobin -----------------------------------------------------------")
                    print(movieurl)
                    tempurl = getdatacontent(movieurl,'sources\s*:\s*\[(.+?)\]')
                    tempurl = tempurl[0].split(',')
                    tempurl = tempurl[-1]
                    tempurl = tempurl.replace('\"','')
                    print (tempurl)
                    temp['title'] = "videobin"
                    temp['url'] = tempurl
                    movielist.append(temp)
                    temp = {}
            except:
                print("unable to fetch Oneload URL")
    print('Movierulz -----------------------------------------------------')
    print('start----------------------------------------------------------')
    print(movielist)
    print('end -----------------------------------------------------------')
    return movielist            


# def appenddatatocatalog(data,id):
#     CATALOG[id] = {}
#     CATALOG[id]['movie'] = []
#     for item in data:
#         temp = {}
#         temp['poster'] = item[0]
#         temp['name'] = item[1] 
#         temp['id'] = id+'_-'+item[1]
#         CATALOG[id]['movie'].append(temp)
#         url = item[2]
#         stream_url = getstreamurl(url)
#         stream_temp={}
#         stream_temp['title'] = 'HTTP URL'
#         if stream_url:
#           if isinstance(stream_url,list):
#               stream_temp['url'] = stream_url[0]
#           if isinstance(stream_url,str):
#               stream_temp['url'] = stream_url
#         else:
#             stream_temp['url'] = ''
#         STREAMS['movie'].update({temp['id']:[stream_temp]})

def appendtamilgundatatocatalog(data,id):
    CATALOG[id] = {}
    CATALOG[id]['movie'] = []
    for item in data:
        temp = {}
        temp['poster'] = item[0]
        temp['name'] = item[1] 
        temp['id'] = id+'_-'+item[1]
        CATALOG[id]['movie'].append(temp)
        url = item[2]
        stream_url = gettamilgunstreamurl(url)
        STREAMS['movie'].update({temp['id']:stream_url})

def appendmovierulzdatatocatalog(data,id):
    CATALOG[id] = {}
    CATALOG[id]['movie'] = []
    for item in data:
        temp = {}
        poster = item[2]
        #poster = poster.replace('https','http')
        #print(poster)
        temp['poster'] = poster
        temp['name'] = item[1] 
        temp['id'] = id+'_-'+item[1]
        CATALOG[id]['movie'].append(temp)
        url = item[0]
        stream_url = getmovierulzstreamurl(url)
        STREAMS['movie'].update({temp['id']:stream_url})





#### Main Program Starts Here #############
global STREAMS
global CATALOG
CATALOG = {}
STREAMS = {}
STREAMS['movie'] = {}
# #TamilGUn site Part Starts Here -------------------------------------------------------------------
# url = "http://tamilgun.com"
# r = requests.get(url) 
# url = r.url
# url = url.split("/")
# url = "http://"+url[2]
# tamilgun_HD_movie = url+"/categories/hd-movies/"
# reg = "<img src=\" (.*?) \" alt=\"(.*?)\" \/>\s+<div class=\"rocky-effect\">\s+<a href=\"(.*?)\" >"
# try:
#     data = getdatacontent(tamilgun_HD_movie,reg)
#     appendtamilgundatatocatalog(data,"tamilgun_HD_movies")
# except:
#     pass
# tamilgun_New_movie = url+"/categories/new-movies-a/"
# reg = "<img src=\" (.*?) \" alt=\"(.*?)\" \/>\s+<div class=\"rocky-effect\">\s+<a href=\"(.*?)\" >"
# try:
#     data = getdatacontent(tamilgun_New_movie,reg)
#     appendtamilgundatatocatalog(data,"tamilgun_New_movies")
# except:
#     pass
# ##TamilGUn site Part Ends Here -------------------------------------------------------------------
##Movierulz site Part Starts Here-----------------------------------------------------------------
url = "http://www.movierulz.com"
r = requests.get(url) 
url = r.url
url = url+"/tamil-movie-free/"
reg = '<a href=\"(.*?)\"\stitle=\"(.*?)\">\s*<img width=\"\d+\" height=\"\d+\" src=\"(.*?)\"'
try:
    data = getdatacontent(url,reg)
    appendmovierulzdatatocatalog(data,"movierulz_tamil")
except:
    pass

##Movierulz site Part Ends Here-------------------------------------------------------------------


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
                'director': 'Links',
                'background': item['poster'],
                'logo':item['poster']
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
        meta['director'] = 'Links:'
        meta['background'] = item['poster']
        meta['logo']:item['poster']
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
    app.run(debug=True)
