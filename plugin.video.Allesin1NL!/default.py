# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Documentaries on YouTube by coldkeys
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#
# Author: coldkeys
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.Allesin1NL!'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')
fanart="http://webneel.com/sites/default/files/images/blog/t-natuwal.jpg"

YOUTUBE_CHANNEL_ID_1 = "UCLFLMHOWrWo0j6BXa2sbzBA/playlists"
YOUTUBE_CHANNEL_ID_2 = "UC1IP4Z_Vk08aRXuund9JABQ/playlists"
YOUTUBE_CHANNEL_ID_3 = "UCRuMH46tSZKjkCgeOtBVJzA/playlists"
YOUTUBE_CHANNEL_ID_4 = "UCFI_PLLqAQeVbV5nKArUjFA/playlists"
YOUTUBE_CHANNEL_ID_5 = "UCgolxyJTkhCUYXDTR758XxA/playlists"
YOUTUBE_CHANNEL_ID_6 = "UCvL4gb8hiw74-Os1hJyCLIg/playlists"
YOUTUBE_CHANNEL_ID_7 = "onlinefilmskijken"
YOUTUBE_CHANNEL_ID_8 = "UCr-JBC1XPqJm_O9iR2M0Wjg/playlists"
YOUTUBE_CHANNEL_ID_9 = "UC_xw6YBnlyLqYnopabbzfiQ/playlists"
YOUTUBE_CHANNEL_ID_10 = "UChVwNC24jIlu98G0rGFtQZQ/playlists"




# Entry point
def run():
    plugintools.log("docu.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    
    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("docu.main_list "+repr(params))

    plugintools.add_item( 
        #action="", 
		title="Live Music",
		url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_1+"/",
		thumbnail="https://archive.org/download/fanart_20170116/Live%20Music%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
		folder=True )
    plugintools.add_item( 
        #action="",
		title="NL Serie ",
		url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_2+"/",
		thumbnail="https://archive.org/download/fanart_20170116/NL%20SERIE%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
		folder=True )
    plugintools.add_item( 
        #action="", 
		title="NL Kids",
		url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_3+"/",
		thumbnail="https://archive.org/download/fanart_20170116/NL%20KIDS%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )
    plugintools.add_item( 
        #action="", 
		title="NL Film",
		url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_4+"/",
		thumbnail="https://archive.org/download/fanart_20170116/NL%20FILM%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )		
    plugintools.add_item( 
        #action="", 
        title="NL Docu",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_5+"/",
        thumbnail="https://archive.org/download/fanart_20170116/NL%20Docu%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
		folder=True )
    plugintools.add_item( 
        #action="", 
        title="NL Cabaret",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_6+"/",
        thumbnail="https://archive.org/download/fanart_20170116/NL%20CABARET%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )
    plugintools.add_item( 
        #action="", 
        title="Xvbmc Handleidingen",
        url="plugin://plugin.video.youtube/user/"+YOUTUBE_CHANNEL_ID_7+"/",
        thumbnail="https://archive.org/download/fanart_20170116/Xvbmc%20handleidingen%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )
    plugintools.add_item( 
        #action="", 
        title="Vlaamse Content",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_8+"/",
        thumbnail="https://archive.org/download/fanart_20170116/Vlaams%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )
    plugintools.add_item( 
        #action="", 
        title="NL Sport",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_9+"/",
        thumbnail="https://archive.org/download/fanart_20170116/NL%20Sport%20icon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )
    plugintools.add_item( 
        #action="", 
        title=".:C.T.R.L:. Gaming Room",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID_10+"/",
        thumbnail="https://archive.org/download/fanart_20170116/CtrlGamingIcon.png",
		fanart="https://archive.org/download/fanart_20170116/fanart.jpg",
        folder=True )		
		


run()
