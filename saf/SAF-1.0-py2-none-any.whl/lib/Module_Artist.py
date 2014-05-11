'''
Created on Sep 20, 2013

@author: karthicm
'''
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
import cirrus_constants
import lib_ParserScript
from lib_Cirrus_PlayerArtist import get_artistcount_from_cirrus,get_artistdetails_from_cirrus
from Module_Songs import get_lastbreadcrumb_elementtext,Validate_Track_DetailView

global global_artist_xpath

def validate_artist_count(wd_handle,UIArtistCount):
    '''
    *********************************************************************
    
    Keyword Name    :Validate Artist Count
    
    Usage           :Function validates the total Artist count returned by CIRRUS service Vs the total Artist Count in the Player for the customer. Example: "Validate Artist Count (wd_handle,25)"
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :09/24/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_cirrus_artist_count = get_artistcount_from_cirrus(wd_handle, cirrus_constants.CIRRUS_API_ARTIST_COUNT_REQUEST_FILE)
        if int(UIArtistCount) == local_cirrus_artist_count:
            print "MSG:Successfully Verified Artists count is '%s' in both CIRRUS and UI!!!" % str(local_cirrus_artist_count)
            local_return_value = True
        else:
            print "Error:Artists count in CIRRUS('%s') and the Artists count in UI ('%s') did not match!!!" % (str(local_cirrus_artist_count),str(UIArtistCount))
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    


def play_validate_artist_view(wd_handle,ArtistName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Artist View
    
    Usage           :Function will validate the Artist 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given ArtistName in Songs View.
                     If ArtistName is not specified, will validate the first Artist by default. 
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :09/24/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_last_breadcrumb_text = get_lastbreadcrumb_elementtext(wd_handle)
        if local_last_breadcrumb_text == 'Artists':
            print "Validating Artists in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_cirrus_artist_metadata = get_artistdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_ARTIST_REQUEST_FILE,ArtistName)
            if not local_cirrus_artist_metadata is None:
                local_return_value = play_validate_artist(wd_handle, local_cirrus_artist_metadata)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Artist('%s') does not exist in the '%s' view." %(ArtistName,local_last_breadcrumb_text))
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Artist view to use "Play Validate Artist View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred: %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_artist(wd_handle,Artist_MetaData):
    """
    *********************************************************************
    Description     : This method will validate the artist and its details view.
    Usage           : Internal module used to validate the metadata, numnber of tracks in artist etc
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
        local_cirrus_artist_objectid = Artist_MetaData.get('objectId')
        global global_artist_xpath
        global_artist_xpath = cirrus_constants.XPATH_ARTIST_1 + str(local_cirrus_artist_objectid)+ cirrus_constants.XPATH_ARTIST_2
        try:
            local_artist_element = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_artist_xpath))
        except:
            local_return_value = False
            raise NoSuchElementException
        #Validate_ArtistName(local_artist_element, Artist_MetaData)
        #Validate_AlbumArtistName(Album_Element, Artist_MetaData)
        local_is_tracks_in_artist_verified = Validate_TracksInArtist(local_artist_element, Artist_MetaData)
        local_is_artist_play_verified = Validate_ArtistPlay(wd_handle, Artist_MetaData)
        if local_is_tracks_in_artist_verified and local_is_artist_play_verified:
            local_return_value = True
        else:
            local_return_value = False
        #Validate_ArtistDetailView(wd_handle, Artist_MetaData)
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Validate_TracksInArtist(Obj_Element,Artist_MetaData):
    """
    *********************************************************************
    Description     : This method will validate the tracks in artist is playable and has proper meta data
    Usage           : Internal Module
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
        local_cirrus_artist_number_of_tracks = Artist_MetaData.get('numTracks')
        local_element_ui_artist_track_count = Obj_Element.find_element_by_xpath(global_artist_xpath + cirrus_constants.XPATH_ARTIST_TRACKS_COUNT)
        local_ui_artist_track_count = local_element_ui_artist_track_count.text
        if local_cirrus_artist_number_of_tracks >1:
            local_cirrus_tracks_count  = (str(local_cirrus_artist_number_of_tracks)+ " items").strip()
        else:
            local_cirrus_tracks_count  = (str(local_cirrus_artist_number_of_tracks)+ " item").strip()
        local_temp_artist_name = Artist_MetaData.get('artistName')
        if (str(local_ui_artist_track_count)).strip() == local_cirrus_tracks_count:
            print "MSG:Successfully validated the number of Tracks('%s') is same in both CIRRUS and UI for the Artist('%s')!!!" %(local_ui_artist_track_count,local_temp_artist_name)
            local_return_value = True
        else:
            print "Error:Number of Tracks in CIRRUS('%s') and Number of Tracks in UI('%s') did not match for Artist('%s')!!!" %(local_cirrus_artist_number_of_tracks,local_ui_artist_track_count,local_temp_artist_name)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred: %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Set_ArtistDetail_AttributeValues(Artist_MetaData):
    """
    *********************************************************************
    Description     : This method will set the run time values for the parameter
    Usage           : Internal Module
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
        lib_ParserScript.global_param_str_attrkey_1 = 'artistName'
        lib_ParserScript.global_param_str_attrvalue_1=Artist_MetaData.get('artistName')
        lib_ParserScript.global_param_str_nextresultstoken =''
        return True
    except:
        return False
    
def Validate_ArtistPlay(wd_handle,Artist_MetaData):
    """
    *********************************************************************
    Description     : This method will validate if the artist is playable
    Usage           : Internal Module
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
        local_xpath_play_sprite = global_artist_xpath + cirrus_constants.XPATH_ARTIST_PLAY_SPRITE
        local_ui_track_play_sprite = wd_handle.find_element_by_xpath(local_xpath_play_sprite)
        local_ui_track_play_sprite.click()
        time.sleep(5)
        local_xpath_artist_image = global_artist_xpath + cirrus_constants.XPATH_ARTIST_IMAGE
        wd_handle.find_element_by_xpath(local_xpath_artist_image).click()
        Set_ArtistDetail_AttributeValues(Artist_MetaData)
        local_artist_play_status = Validate_Track_DetailView(wd_handle,'Artists','', True)
        local_temp_artist_name = Artist_MetaData.get('artistName')
        if local_artist_play_status:
            print "Successfully validated that the selected Artist('%s') is playing" %local_temp_artist_name
            return True
        else:
            print "Error: Could not play the selected Artist('%s')" %local_temp_artist_name
            return False
    except Exception as ex:
        print ex
        return False