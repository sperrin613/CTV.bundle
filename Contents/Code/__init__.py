NAME            = "CTV"
PLUGIN_PREFIX   = "/video/ctv"

RE_EPISODE_ID = Regex('PlayEpisode\(([0-9]+).+?\)')

URL             = 'http://watch.%s/'
LIBRARY_URL     = 'http://watch.%s/library/'
CLIP_LOOKUP     = 'http://watch.%s/AJAX/ClipLookup.aspx?episodeid=%s'

NETWORK = {'title' : 'CTV', 'network' : 'ctv.ca'}

####################################################################################################
def Start():
    ObjectContainer.title1  = NAME

####################################################################################################
@handler(PLUGIN_PREFIX, NAME)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(GetFeatured), title="Featured"))
    oc.add(DirectoryObject(key=Callback(GetVideoLibrary, level=1, url=(URL % NETWORK['network'])+'library/', title2='Video Library'), title="Video Library"))
    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/library', level=int, title1=str, title2=str)
def GetVideoLibrary(url, level, title1=None, title2=''):
    if title1:
        oc = ObjectContainer(title1=title1, title2=title2)
    else:
        oc = ObjectContainer(title2=title2)
    for show in HTML.ElementFromURL(url).xpath('.//div[@id="Level%d"]/ul/li' % level):
        title = None
        url = url    
        try: title = show.find('a').get('title')
        except: pass
        try: url = show.find('a').get('href')
        except: pass
        playable = ''
        try: playable = show.xpath('.//dd[@class="Play"]/a')[0].get('title')
        except: pass
        if playable:
            try: title = show.xpath('.//dl[@class="Item"]/dt/a')[0].text
            except:pass
            try: summary =  show.xpath('.//dd[@class="Description"]')[0].text 
            except: summary ="No Summary Available"
            episode_id = RE_EPISODE_ID.search(show.xpath('.//dd[@class="Play"]/a')[0].get('href')).group(1)
            thumb =  show.xpath('.//dd[@class="Thumbnail"]/a/img')[0].get('src')
            oc.add(VideoClipObject(url=url+'#full-episode-%s' % episode_id, title=title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb.replace('/80/60/', '/560/420/'))))
        else:
            oc.add(DirectoryObject(key=Callback(GetVideoLibrary, level=level+1, url=url, title2=title, title1=title2), title=title))
    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/featured')
def GetFeatured():
    oc = ObjectContainer(title2='Featured')
    page = HTML.ElementFromURL((URL % NETWORK['network']) + 'featured/')
    for show in page.xpath('//div[@class="Frame"]/ul/li'):    
        try:
            item = show.xpath('.//dl[@class="Item"]')[0]
            title = item.find('dt/a').get('title')
            url = item.find('dt/a').get('href')
            episode_id = RE_EPISODE_ID.search(show.xpath('.//dd[@class="Play"]/a')[0].get('onclick')).group(1)
            try: summary = item.find('dd[@class="Description"]').text
            except: summary = "No Summary Available"
            thumb =  item.find('dd[@class="Thumbnail"]/a/img').get('src')
            oc.add(VideoClipObject(url=url+'#full-episode-%s' % episode_id, title=title, summary=summary,
                thumb=Resource.ContentsOfURLWithFallback(url=thumb.replace('/80/60/', '/560/420/'))))
        except:
            pass
    return oc
