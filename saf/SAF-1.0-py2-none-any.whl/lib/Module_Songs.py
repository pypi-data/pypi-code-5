'''
Created on Aug 28, 2013

@author: karthicm
'''
from lib_Cirrus_PlayerTracks import get_songscount_from_cirrus
from lib_Cirrus_PlayerTracks import get_trackdetails_from_cirrus
from selenium.webdriver.support.wait import WebDriverWait
from lib_Operations_Common import ConvertToSeconds
import time
from selenium.common.exceptions import NoSuchElementException
import lib_ParserScript
import cirrus_constants

global global_track_xpath

def validate_songs_count(wd_handle,UISongsCount):
    '''
    *********************************************************************
    
    Keyword Name    :Validate Songs Count
    
    Usage           :Function validates the total songs count returned by CIRRUS service Vs the total songs Count in the Player. Example: "Validate Songs Count (wd_handle,253)"
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/28/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_cirrus_track_count = get_songscount_from_cirrus(wd_handle, cirrus_constants.CIRRUS_API_TRACKS_COUNT_REQUEST_FILE)
        if float(UISongsCount) == float(local_cirrus_track_count):
            print "MSG:Successfully Verified Songs count is '%s' in both CIRRUS and UI!!!" % str(local_cirrus_track_count) 
            local_return_value = True
        else:
            print "Error:Songs count in CIRRUS('%s') and the Songs count in UI ('%s') did not match!!!" %(str(local_cirrus_track_count),str(UISongsCount))
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def get_lastbreadcrumb_elementtext(wd_handle):
    try:
        #BreadCrumb_XPath = "//*[@id='breadcrumbs']/li/span[@class='lastCrumb']"
        local_element_last_breadcrumb = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(cirrus_constants.XAPTH_LAST_BREADCRUMB))
        local_last_breadcrumb_text = local_element_last_breadcrumb.text
        return local_last_breadcrumb_text
    except:
        return False

def select_track_songs_view(wd_handle,TrackName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Select Track Songs View
    
    Usage           :Function will select the tracks with the given TrackName in Songs View.
                     If TrackName is not specified, will select the first track by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :09/17/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Songs':
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_TRACKS_REQUEST_FILE,TrackName)
            #print local_track_meta_data
            if not local_track_meta_data is None:
                local_cirrus_track_id = local_track_meta_data.get('objectId')
                global global_track_xpath
                global_track_xpath = "//tr[@uid='"+str(local_cirrus_track_id)+"']"
                try:
                    local_element_track = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_track_xpath))
                except:
                    local_return_value = False
                    raise NoSuchElementException
                local_return_value = Validate_TrackCheckBox(local_element_track,True)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Song does not exist in the '%s' view." %local_last_breadcrumb_text)
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Songs view to use "Play Validate Track Songs View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception: %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_track_songs_view(wd_handle,TrackName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Track Songs View
    
    Usage           :Function will validate the tracks 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given TrackName in Songs View.
                     If TrackName is not specified, will validate the first track by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/28/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Songs':
            print "Validating Tracks in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_TRACKS_REQUEST_FILE,TrackName)
            #print local_track_meta_data
            if not local_track_meta_data is None:
                local_return_value = play_validate_track(wd_handle, local_track_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Songs does not exist in the '%s' view." %local_last_breadcrumb_text)
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Songs view to use "Play Validate Track Songs View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception: %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_track_recentlyadded_View(wd_handle,TrackName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Track Recentlyadded View
    
    Usage           :Function will validate the tracks 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given TrackName in Recentlyadded View.
                     If TrackName is not specified, will validate the first track by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/28/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Recently Added':
            print "Validating Tracks in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            lib_ParserScript.global_param_str_attrvalue_1 = cirrus_constants.RECENTLYADDED_PLAYLISTID
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_SMARTPLAYLIST_REQUEST_FILE,TrackName)
            if not local_track_meta_data is None:
                local_return_value = play_validate_track(wd_handle, local_track_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Songs does not exist in the '%s' view." %local_last_breadcrumb_text)
                local_return_value = False      
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Songs view to use "Play Validate Track Recently added View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_track_purchased_view(wd_handle,TrackName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Track Purchased View
    
    Usage           :Function will validate the tracks 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given TrackName in Purchased View.
                     If TrackName is not specified, will validate the first track by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/28/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Purchased':
            print "Validating Tracks in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            lib_ParserScript.global_param_str_attrvalue_1 = cirrus_constants.PURCHASED_PLAYLISTID
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_SMARTPLAYLIST_REQUEST_FILE,TrackName)
            if not local_track_meta_data is None:
                local_return_value = play_validate_track(wd_handle, local_track_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Songs does not exist in the '%s' view." %local_last_breadcrumb_text)
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Purchased view to use "Play Validate Track Purchased View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def play_validate_track_imported_view(wd_handle,TrackName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Track Imported View
    
    Usage           :Function will validate the tracks 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given TrackName in Imported View.
                     If TrackName is not specified, will validate the first track by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/28/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Imported':
            print "Validating Tracks in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            lib_ParserScript.global_param_str_attrvalue_1 = cirrus_constants.IMPORTED_PLAYLISTID
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_SMARTPLAYLIST_REQUEST_FILE,TrackName)
            if not local_track_meta_data is None:
                local_return_value = play_validate_track(wd_handle, local_track_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Songs does not exist in the '%s' view." %local_last_breadcrumb_text)
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Purchased view to use "Play Validate Track Imported View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value


def Validate_Track_DetailView(wd_handle,DetailView,TrackName='',OnlyPlay = False):
    """
    *********************************************************************
    Description     : This method will validate the track detail view.
    Usage           : Used to validate the track detail view and all associated metat data
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if DetailView == 'Albums':
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALBUMTRACKS_REQUEST_FILE,TrackName)
        elif DetailView == 'Artists':
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ARTISTSTRACKS_REQUEST_FILE,TrackName)
        elif DetailView == 'ArtistsAlbum':
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ARTISTSALBUMSTRACKS_REQUEST_FILE,TrackName)
        elif DetailView == 'Genres':
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_GENRESTRACKS_REQUEST_FILE,TrackName)
        elif DetailView == 'GenresAlbum':
            local_track_meta_data = get_trackdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_GENRESALBUMSTRACKS_REQUEST_FILE,TrackName)
        if not local_track_meta_data is None:
            if not OnlyPlay:
                local_return_value = play_validate_track(wd_handle, local_track_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                try:
                    local_cirrus_track_id = local_track_meta_data.get('objectId')
                    global global_track_xpath
                    global_track_xpath = "//tr[@uid='"+str(local_cirrus_track_id)+"']"
                    local_element_track = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_track_xpath))
                except:
                    raise NoSuchElementException
                    local_return_value = False
                local_return_value = Validate_TrackPlay(local_element_track)
                lib_ParserScript.global_param_str_nextresultstoken = ''
        else:
            raise Exception("Error:Selected Songs does not exist in the '%s' view." %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value


def play_validate_track(wd_handle,Track_MetaData):
    """
    *********************************************************************
    Description     : This method will validate the track and all related information.
    Usage           : Internal module used to validate the meta data
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_cirrus_track_id = Track_MetaData.get('objectId')
        global global_track_xpath
        global_track_xpath = cirrus_constants.XPATH_TRACK_1 + str(local_cirrus_track_id) + cirrus_constants.XPATH_TRACK_2
        local_cirrus_track_title = Track_MetaData.get('title')
        local_cirrus_track_album = Track_MetaData.get('albumName')
        local_cirrus_track_artist = Track_MetaData.get('artistName')
        local_cirrus_track_duration = Track_MetaData.get('duration')
        try:
            local_element_track = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_track_xpath))
        except:
            local_return_value = False
            raise NoSuchElementException
        local_is_checkbox_selected = Validate_TrackCheckBox(local_element_track)
        local_is_track_playing = Validate_TrackPlay(local_element_track)
        local_is_track_title_same = Validate_TrackTitle(local_element_track, local_cirrus_track_title)
        local_is_track_album_same = Validate_TrackAlbum(local_element_track, local_cirrus_track_album)
        local_is_track_artist_same = Validate_TrackArtist(local_element_track, local_cirrus_track_artist)
        local_is_track_duration_same = Validate_TrackDuration(local_element_track, local_cirrus_track_duration)
        if local_is_checkbox_selected and local_is_track_playing and local_is_track_title_same and local_is_track_album_same and local_is_track_artist_same and local_is_track_duration_same:
            local_return_value = True
        else:
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Validate_TrackDuration(Obj_Element,Cirrus_Track_Duration):
    """
    *********************************************************************
    Description     : This method will validate the track duration.
    Usage           : Used to validate the track duration displayed in UI against the CIRRUS returned data
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_element_ui_track_duration = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_DURATION)
        local_ui_track_duration_minute = local_element_ui_track_duration.text
        local_ui_track_duration_seconds = ConvertToSeconds(local_ui_track_duration_minute)
        if str(local_ui_track_duration_seconds) == str(Cirrus_Track_Duration):
            print "MSG:Successfully validated the Track duration(%s) is same in both UI and CIRRUS!!!" %local_ui_track_duration_minute
            local_return_value = True
        else:
            print "Error:Track duration in CIRRUS('%s') and Track duration in UI('%s') did not match!!!" %(Cirrus_Track_Duration,local_ui_track_duration_seconds)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def Validate_TrackArtist(Obj_Element,Cirrus_Track_Artist):
    """
    *********************************************************************
    Description     : This method will validate the track artist name.
    Usage           : Used to validate the track artist name in UI against CIRRUS returned data
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_element_ui_track_artist = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_ARTIST)
        local_ui_track_artist = local_element_ui_track_artist.get_attribute('title')
        if str(local_ui_track_artist) == str(Cirrus_Track_Artist):
            print "MSG:Successfully validated the Track Artist(%s) is same in both UI and CIRRUS!!!" %local_ui_track_artist
            local_return_value = True
        else:
            print "Error:Track Artist in CIRRUS('%s') and Track Artist in UI('%s') did not match!!!" %(Cirrus_Track_Artist,local_ui_track_artist)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def Validate_TrackAlbum(Obj_Element,Cirrus_Track_Album):
    """
    *********************************************************************
    Description     : This method will validate the album of the track.
    Usage           : Used to validate the tracks album
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_element_ui_track_album = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_ALBUM)
        local_ui_track_album = local_element_ui_track_album.get_attribute('title')
        if str(local_ui_track_album) == str(Cirrus_Track_Album):
            print "MSG:Successfully validated the Track Album(%s) is same in both UI and CIRRUS!!!" %local_ui_track_album
            local_return_value = True
        else:
            print "Error:Track Album in CIRRUS('%s') and Track Album in UI('%s') did not match!!!" %(Cirrus_Track_Album,local_ui_track_album)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def Validate_TrackTitle(Obj_Element,Cirrus_Track_Title):
    """
    *********************************************************************
    Description     : This method will validate the track title.
    Usage           : Used to validate the ui title of the track against the CIRRUS value
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_element_ui_track_title = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_TITLE)
        local_ui_track_title = local_element_ui_track_title.get_attribute('title')
        if str(local_ui_track_title) == str(Cirrus_Track_Title):
            print "MSG:Successfully validated the Track Title(%s) is same in both UI and CIRRUS!!!" %local_ui_track_title
            local_return_value = True
        else:
            print "Error:Track title in CIRRUS('%s') and Track title in UI('%s') did not match!!!" %(Cirrus_Track_Title,local_ui_track_title)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def Validate_TrackPlay(Obj_Element):
    """
    *********************************************************************
    Description     : This method will validate if the track is playable
    Usage           : Used to validate the track play feature
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_track_index = Obj_Element.get_attribute('idx')
        local_xpath_track_play_sprite = cirrus_constants.XPATH_TRACK_PLAY_SPRITE_1 + str(local_track_index)+ cirrus_constants.XPATH_TRACK_PLAY_SPRITE_2
        local_ui_track_play_sprite = Obj_Element.find_element_by_xpath(local_xpath_track_play_sprite)
        local_ui_track_play_sprite.click()
        time.sleep(5)
        local_class_first_track_play_sprite = local_ui_track_play_sprite.get_attribute('class')
        if local_class_first_track_play_sprite == 'nowPlaying':
            print "MSG:Successfully playing the track from Sprite play button!!!"
            return True
        else:
            print "Error:Could not play the track from sprite play button!!!"
            return False
    except Exception as ex:
        print "Exception:Could not play the track from sprite play button and the exception is %s !!!" %ex
        return False
        
def Validate_DropDown(Obj_Element):
    """
    *********************************************************************
    Description     : This method will validate the track drop down is accessible.
    Usage           : Used to validate the track drop down is accessible
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_ui_track_drop_down = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_DROPDOWN)
        local_ui_track_drop_down.click()
    except Exception as ex:
        print "Exception:Could not play the track from sprite play button and the exception is %s !!!" %ex
        return False

def Validate_TrackCheckBox(Obj_Element,LeaveSelected = False):
    """
    *********************************************************************
    Description     : This method will validate if the track check box is selectable.
    Usage           : Used to validate the track check box is selectable
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/16/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_ui_track_checkbox = Obj_Element.find_element_by_xpath(global_track_xpath + cirrus_constants.XPATH_TRACK_CHECKBOX)
        local_ui_track_checkbox.click()
        if local_ui_track_checkbox.is_selected():
            if not LeaveSelected:
                local_ui_track_checkbox.click()
                print "MSG:Track Check box selected & unselected successfully!!!"
            else:
                print "MSG:Track Check box selected successfully!!!"
        return True
    except Exception as ex:
        print "Exception:Could not select the Check box for the Track and the Exception is %s" %ex
        return False