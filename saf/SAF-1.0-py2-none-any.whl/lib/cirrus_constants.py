"""
*********************************************************************
Description     :This module will hold all the constants required for CIRRUS integration with Cloud Player Web, Morpho & other clients
Usage           :
Return Value    :NA
ToDo            :NA
=====================================================================
Created By          :Karthick Mani
Created Date        :01/08/2013
Last Modified By    :
Last Modified Date  :
*********************************************************************
"""

CIRRUS_LIBRARY_URL = 'http://cirrus-library.amazon.com/internal/2011-06-01/!'
CIRRUS_API_MAINDIRECTORY = "C:\SAF\lib\Json\CPWeb"
CIRRUS_API_ALL_ALBUMS_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY + "\\albums\CIRRUS_API_SelectAlbums_All.txt"
CIRRUS_API_ALBUMS_COUNT_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY+ "\\albums\CIRRUS_API_SelectAlbums_CountOnly.txt"
CIRRUS_API_ARTISTSALBUM_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY+"\\artist\CIRRUS_API_SelectAlbums_DetailViews.txt"
CIRRUS_API_ARTISTSALBUM_COUNT_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY+"\\artist\CIRRUS_API_SelectAlbums_DetailView_CountOnly.txt"
CIRRUS_API_GENRESALBUM_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY +"\\genres\CIRRUS_API_SelectAlbums_DetailViews.txt"
CIRRUS_API_GENRESALBUM_COUNT_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY+"\\genres\CIRRUS_API_SelectAlbums_DetailView_CountOnly.txt"
CIRRUS_API_ALL_ARTIST_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY +"\\artist\CIRRUS_API_SelectArtists_All.txt"
CIRRUS_API_ARTIST_COUNT_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY +"\\artist\CIRRUS_API_SelectArtists_CountOnly.txt"
CIRRUS_API_ALL_GENRES_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY+"\\genres\CIRRUS_API_SelectGenres_All.txt"
CIRRUS_API_GENRES_COUNT_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY+"\\genres\CIRRUS_API_SelectGenres_CountOnly.txt"
CIRRUS_API_ALL_TRACKS_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY + "\\tracks\CIRRUS_API_SelectTracks_All.txt"
CIRRUS_API_TRACKS_COUNT_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY+ "\\tracks\CIRRUS_API_SelectTracks_CountOnly.txt"
CIRRUS_API_SMARTPLAYLIST_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY + "\\smartplaylist\CIRRUS_API_getSmartPlaylist.txt"
CIRRUS_API_ALBUMTRACKS_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY + "\\albums\CIRRUS_API_SelectTracks_DetailView.txt"
CIRRUS_API_ALBUMTRACKS_COUNT_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY + "\\albums\CIRRUS_API_SelectTracks_DetailView_CountOnly.txt"
CIRRUS_API_ARTISTSALBUMSTRACKS_REQUEST_FILE  = CIRRUS_API_MAINDIRECTORY +  "\\artist\CIRRUS_API_SelectAlbums_SelectTracks_DetailView.txt"
CIRRUS_API_ARTISTSTRACKS_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY +  "\\artist\CIRRUS_API_SelectTracks_DetailView.txt"
CIRRUS_API_GENRESTRACKS_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY + "\\genres\CIRRUS_API_SelectTracks_DetailView.txt"
CIRRUS_API_GENRESALBUMSTRACKS_REQUEST_FILE = CIRRUS_API_MAINDIRECTORY + "\\genres\CIRRUS_API_SelectAlbums_SelectTracks_DetailView.txt"
IMPORTED_PLAYLISTID = "IMPORTED-V0-OBJECTID"
PURCHASED_PLAYLISTID= "PURCHASES-V0-OBJECTID"
RECENTLYADDED_PLAYLISTID ="RECENTLY-ADDED-V0-OBJECTID"

# XPATH CONSTANTS

XAPTH_LAST_BREADCRUMB = "//*[@id='breadcrumbs']/li/span[@class='lastCrumb']"

XPATH_TRACK_1 = "//tr[@uid='"
XPATH_TRACK_2 = "']"
XPATH_TRACK_DURATION = "/td[@class='durationCell']"
XPATH_TRACK_ARTIST = "/td[@class='artistCell']"
XPATH_TRACK_ALBUM = "/td[@class='albumCell']"
XPATH_TRACK_TITLE = "/td[@class='titleCell']"
XPATH_TRACK_CHECKBOX = "/td/input[@class='checkbox']"
XPATH_TRACK_DROPDOWN = "/td/input[@class='optionSprite']"
XPATH_TRACK_PLAY_SPRITE_1 = "//td/a[@href='#play/song=/idx="
XPATH_TRACK_PLAY_SPRITE_2 = "']"
XPATH_TRACK_CHECKBOX_1 = "//tr[@idx='"
XPATH_TRACK_CHECKBOX_2 = "']/td/input[@class='checkbox']"

XPATH_GENRES_1 = "//*[@class='genre itemTitle'][text()= '"
XPATH_GENRES_2 = "']"
XPATH_GENRES_TRACK_COUNT = "/../div[@class='albumSongCount']"
XPATH_GENRES_PLAY_SPRITE = "/../*/a[@class='albumArtMp3PlaySprite playAlbum']"
XPATH_GENRES_IMAGE = "/..//*[contains(@class,'albumImage medium')]"
XPATH_GENRES_GRID_1 = "//*[@id='gridBuffer']//li[@item='"
XPATH_GENRES_GRID_2 = "']"

XPATH_ARTIST_1 = "//*/a[contains(@href,'"
XPATH_ARTIST_2 = "')]"
XPATH_ARTIST_TRACKS_COUNT = "/../../div[@class='albumSongCount']"
XPATH_ARTIST_PLAY_SPRITE = "/../../div/a[@class='albumArtMp3PlaySprite playAlbum']"
XPATH_ARTIST_IMAGE = "/../..//*[contains(@class,'albumImage medium')]"
XPATH_ARTIST_GRID_1 = "//*[@id='gridBuffer']//li[@item='"
XPATH_ARTIST_GRID_2 = "']"

XPATH_ALBUM_1 = "//*/a[contains(@href,'"
XPATH_ALBUM_2 = "')]"
XPATH_ALBUM_IMAGE = "/../..//img[@class='albumImage medium']"
XPATH_ALBUM_TITLE = "//div[@id='selectedAlbum']//div[@class='albumTitle']/strong"
XPATH_ALBUM_ARTIST_NAME = "//div[@id='selectedAlbum']//div[@class='artist']/a"
XPATH_ALBUM_RELEASE_DATE = "//div[@id='selectedAlbum']//div[@class='releaseDate']"
XPATH_ALBUM_RECOMMEND_MORE = "//div[@id='selectedAlbum']//div[@class='moreLikeThis']/a"
XPATH_ALBUM_FB_SHARE = "//div[@id='selectedAlbum']//span[@class='shareButton facebookSprite']"
XPATH_ALBUM_TWITTER_SHARE = "//div[@id='selectedAlbum']//span[@class='shareButton twitterSprite']"
XPATH_ALBUM_PLAY_SPRITE = "/../../div/a[@class='albumArtMp3PlaySprite playAlbum']"
XPATH_ALBUM_IMAGE_1 = "/../..//*[contains(@class,'albumImage medium')]"
XPATH_ALBUM_GRID = "/../../div[@class='gridOptions']/a"
XPATH_ALBUM_TRACKS_COUNT = "/../../div[@class='albumSongCount']"
XPATH_ALBUM_NAME = "/../../div[@class='albumTitle itemTitle']"
XPATH_ALBUM_ARTIST = "/../../div[@class='artist']"
XPATH_ALBUM_GRID_1 = "//*[@id='gridBuffer']//li[@item='"
XPATH_ALBUM_GRID_2 = "']"