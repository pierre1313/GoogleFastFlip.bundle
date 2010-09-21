# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re

####################################################################################################

PLUGIN_PREFIX           = "/photos/googlefastflip"
PLUGIN_ID               = "com.plexapp.plugins.googlefastflip"
PLUGIN_REVISION         = 0.1
PLUGIN_UPDATES_ENABLED  = True

GFF_URL = 'http://fastflip.googlelabs.com'

NAME = L('Google Fast Flip')

ART           = 'art-default.png'
ICON          = 'icon-default.png'

CACHE_TIME = 3600

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(PLUGIN_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
    
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def CreatePrefs():
    Prefs.Add(id='username', type='text', default='', label='Your Username')
    Prefs.Add(id='password', type='text', default='', label='Your Password', option='hidden')

def ValidatePrefs():
    u = Prefs.Get('username')
    p = Prefs.Get('password')
    ## do some checks and return a
    ## message container
    if( u and p ):
        return MessageContainer(
            "Success",
            "User and password provided ok"
        )
    else:
        return MessageContainer(
            "Error",
            "You need to provide both a user and password"
        )
        
def UpdateCache():
    HTTP.PreCache(GFF_URL , CACHE_TIME)
    HTTP.PreCache(GFF_URL + "/rss?q=view:popular" , CACHE_TIME)
    HTTP.PreCache(GFF_URL + "/rss?q=view:recent" , CACHE_TIME)
    HTTP.PreCache(GFF_URL + "/rss?q=view:controversial" , CACHE_TIME)
    HTTP.PreCache(GFF_URL + "/rss?q=view:headlines" , CACHE_TIME) 
    GetCollectionsMenu(ItemInfoRecord())
        
def VideoMainMenu():

    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(RSS_parser,"Popular"),pageurl = GFF_URL + "/rss?q=view:popular" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Recent"),pageurl = GFF_URL + "/rss?q=view:recent" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Controversial"),pageurl = GFF_URL + "/rss?q=view:controversial" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Headlines"),pageurl = GFF_URL + "/rss?q=view:headlines" ))    
    dir.Append(Function(DirectoryItem(Sections,"Sections")))
    dir.Append(Function(DirectoryItem(Topics,"Topics")))
    return dir
    
def Sections(sender):

    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(RSS_parser,"Politics"),pageurl = GFF_URL + "/rss?q=section%3APolitics" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"World"),pageurl = GFF_URL + "/rss?q=section%3AU.S." ))
    dir.Append(Function(DirectoryItem(RSS_parser,"U.S."),pageurl = GFF_URL + "/rss?q=section%3AWorld" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Sports"),pageurl = GFF_URL + "/rss?q=section%3ASports" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Sci/Tech"),pageurl = GFF_URL + "/rss?q=section%3ASci/Tech" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Entertainment"),pageurl = GFF_URL + "/rss?q=section%3AEntertainement" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Health"),pageurl = GFF_URL + "/rss?q=section%3AHealth" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Opinion"),pageurl = GFF_URL + "/rss?q=section%3AOpinion" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Travel"),pageurl = GFF_URL + "/rss?q=section%3ATravel" ))
    dir.Append(Function(DirectoryItem(RSS_parser,"Environment"),pageurl = GFF_URL + "/rss?q=section%3AEnvironment" ))
    return dir


def Topics(sender):
    dir = MediaContainer(viewGroup="List")
    for topic in XML.ElementFromURL(GFF_URL,True).xpath("//div[@id='l2']"):
      for element in topic.xpath("a"):
        dir.Append(Function(DirectoryItem(RSS_parser,element.text),pageurl = GFF_URL + element.get("href").replace("search","rss")))
    return dir

def RSS_parser(sender, pageurl , replaceParent=False):
    tags = RSS.FeedFromString(HTTP.Request(pageurl))
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="Coverflow", replaceParent=replaceParent)
    
    for tag in tags["entries"]:
      for e in XML.ElementFromString(tag["summary_detail"]["value"], isHTML='True').xpath("a/img"):
        thumb = e.get("src")
        image = unicode(re.sub("-tiny","",thumb),'utf-8')
        if thumb != None:
          dir.Append(PhotoItem(key=image, title='',summary='',thumb=thumb))
    return dir
