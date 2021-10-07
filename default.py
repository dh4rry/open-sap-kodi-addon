import json
import requests
from bs4 import BeautifulSoup
import requests.sessions
import routing
import xbmcgui
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

plugin = routing.Plugin()

s = requests.Session()

def login():
    addon = xbmcaddon.Addon('plugin.video.open_sap')
    user = addon.getSetting('Username')
    pw = addon.getSetting('Password')
    r = s.get('https://open.sap.com/sessions/new')
    soup = BeautifulSoup(r.content, 'html.parser')
    auth_token = soup.find("input", { "name": "authenticity_token"} )['value']
    payload = { "authenticity_token": auth_token, 'login[email]': user, 'login[password]': pw, 'login[redirect_url]': "/dashboard"}
    r = s.post('https://open.sap.com/sessions', data=payload)

login()

@plugin.route('/')
def get_enrollments():
    r = s.get('https://open.sap.com/api/v2/courses?include=channel%2Cuser_enrollment')
    j = json.loads(r.content)
    enrollments = []
    found = False
    for data in j['data']:
        if 'user_enrollment' in data['relationships']:
            found = True
            addDirectoryItem(plugin.handle, plugin.url_for(show_course, data['id']), ListItem(data['attributes']['title']), True)
            print(data['id'])

    if found == False:
        addDirectoryItem(plugin.handle, 'plugin://plugin.video.open_sap/', ListItem('No enrollment or wrong login data'), True)
    
    endOfDirectory(plugin.handle)

@plugin.route('/show_course/<course_id>')
def show_course(course_id):
    r = s.get('https://open.sap.com/api/v2/course-items?filter[course]=' + course_id)
    j = json.loads(r.content)
    for data in j['data']:
        if data['attributes']['content_type'] == 'video':
            show_stream(data['relationships']['content']['data']['id'], data['attributes']['title'])
    endOfDirectory(plugin.handle)

def show_stream(video_id, title):
    r = s.get('https://open.sap.com/api/v2/videos/' + video_id)
    j = json.loads(r.content)
    liz = xbmcgui.ListItem( title, iconImage='', thumbnailImage=j['data']['attributes']['single_stream']['thumbnail_url'])
    infoLabels = {"Title": 	title}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    addDirectoryItem(handle=plugin.handle, url=j['data']['attributes']['single_stream']['hd_url'], listitem=liz)


#print('enrollments:')
#get_enrollments()
#print('video_items:')
#get_video_items('06077148-9304-4fce-b9b8-fc05d146bfe3')
if __name__ == '__main__':
    plugin.run()
