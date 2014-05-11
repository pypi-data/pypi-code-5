'''
Created on Aug 29, 2013

@author: karthicm
'''

from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
import cirrus_constants
import lib_ParserScript
from lib_Cirrus_PlayerAlbums import get_albumcount_from_cirrus, get_albumdetails_from_cirrus
from Module_Songs import get_lastbreadcrumb_elementtext
from lib_Operations_Common import return_datetimeformat
from Module_Songs import Validate_Track_DetailView
from lib_TestSetUp import is_element_present

global global_album_xpath
global global_cirrus_album_name

def validate_albums_count(wd_handle,UIAlbumsCount):
    '''
    *********************************************************************
    
    Keyword Name    :Validate Albums Count
    
    Usage           :Function validates the total Albums count returned by CIRRUS service Vs the total Albums Count in the Player for the customer. Example: "Validate Album Count (wd_handle,25)"
    
    Return Value    :Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :08/29/2013
    
    Last Modified By    :
    
    Last Modified Date  :
    
    *********************************************************************
    '''
    try:
        local_cirrus_album_count = get_albumcount_from_cirrus(wd_handle, cirrus_constants.CIRRUS_API_ALBUMS_COUNT_REQUEST_FILE)
        if int(UIAlbumsCount) == local_cirrus_album_count:
            print "MSG:Successfully Verified Albums count is '%s' in both CIRRUS and UI!!!" % str(local_cirrus_album_count)
            local_return_value = True
        else:
            print "Error:Albums count in CIRRUS('%s') and the Albums count in UI ('%s') did not match!!!" %(str(local_cirrus_album_count),str(UIAlbumsCount))
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def download_album_in_albumview(wd_handle,AlbumName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Download Album In AlbumView
    
    Usage           :Function will download the'Album' Album View.
                     If Album name is not specified, will download the first album by default. 
    
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
        if local_last_breadcrumb_text == 'Albums':
            print "Validating Albums in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_cirrus_album_metadata = get_albumdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_ALBUMS_REQUEST_FILE,AlbumName)
            if not local_cirrus_album_metadata is None:
                local_cirrus_album_objectid = local_cirrus_album_metadata.get('objectId')
                global global_album_xpath
                global_album_xpath = cirrus_constants.XPATH_ALBUM_1 + str(local_cirrus_album_objectid) + cirrus_constants.XPATH_ALBUM_2
                local_download_status = Download_Album_GridOptions(wd_handle, local_cirrus_album_metadata)
                lib_ParserScript.global_param_str_nextresultstoken = ''
                local_return_value = local_download_status
            else:
                raise Exception("Error:Selected Album('%s') does not exist in the '%s' view." %(AlbumName,local_last_breadcrumb_text))
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Album view to use "Play Validate Album View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_album_view(wd_handle,AlbumName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Album View
    
    Usage           :Function will validate the Album 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given AlbumName in Songs View.
                     If AlbumName is not specified, will validate the first Album by default. 
    
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
        if local_last_breadcrumb_text == 'Albums':
            print "Validating Albums in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_cirrus_album_metadata = get_albumdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_ALBUMS_REQUEST_FILE,AlbumName)
            if not local_cirrus_album_metadata is None:
                local_album_validation_status = play_validate_album(wd_handle, local_cirrus_album_metadata)
                lib_ParserScript.global_param_str_nextresultstoken = ''
                local_return_value = local_album_validation_status
            else:
                raise Exception("Error:Selected Album('%s') does not exist in the '%s' view." %(AlbumName,local_last_breadcrumb_text))
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Album view to use "Play Validate Album View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_album(wd_handle,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate the album and its details view.
    Usage           : Internal module used to validate the metadata, numnber of tracks in album etc
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
        local_cirrus_album_objectid = Cirrus_Album_Metadata.get('objectId')
        global global_album_xpath
        global_album_xpath = cirrus_constants.XPATH_ALBUM_1 + str(local_cirrus_album_objectid) + cirrus_constants.XPATH_ALBUM_2
        try:
            local_album_element = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_album_xpath))
        except:
            local_return_value = False
            raise NoSuchElementException
        local_is_album_name_verified = Validate_AlbumName(local_album_element, Cirrus_Album_Metadata)
        local_is_albumartist_name_verified = Validate_AlbumArtistName(local_album_element, Cirrus_Album_Metadata)
        local_is_tracks_in_album_verified = Validate_TracksInAlbum(local_album_element, Cirrus_Album_Metadata)
        local_is_album_play_verified = Validate_AlbumPlay(wd_handle, Cirrus_Album_Metadata)
        local_is_album_detail_view_verified = Validate_AlbumDetailView(wd_handle, Cirrus_Album_Metadata)
        if local_is_album_name_verified and local_is_albumartist_name_verified and local_is_tracks_in_album_verified and local_is_album_play_verified and local_is_album_detail_view_verified:
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
        

def Validate_AlbumReleaseDate(UI_AlbumReleaseDate,Cirrus_Album_AlbumReleaseDate):
    """
    *********************************************************************
    Description     : This method will validate the album release date.
    Usage           : Used to validate the album release date in CIRRUS against the UI data
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
        local_cirrus_album_release_date = return_datetimeformat(Cirrus_Album_AlbumReleaseDate)
        local_temp_cirrus_album_release_date = (str(local_cirrus_album_release_date)).split(' ')
        local_temp_ui_album_release_date = (str(UI_AlbumReleaseDate)).split(' ')
        if local_temp_cirrus_album_release_date[-1] == local_temp_ui_album_release_date[-1]:
            print "MSG:Album release date matched the date(%s) in both CIRRUS and UI" %UI_AlbumReleaseDate
            local_return_value = True
        else:
            print "Error: Album release date did not match the UI date(%s) and CIRRUS date(%s)" %(UI_AlbumReleaseDate,local_cirrus_album_release_date)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def Validate_AlbumDetailView(wd_handle,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate the album detail view.
    Usage           : Used to validate the album detail view, like album name, social app options, recommendations etc through dynamic locator
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
        local_return_value = True
        try:
            local_xpath_album_image = global_album_xpath + cirrus_constants.XPATH_ALBUM_IMAGE
            local_ui_album_image = wd_handle.find_element_by_xpath(local_xpath_album_image)
            local_ui_album_image.click()
        except:
            pass
        local_navigated_album = get_lastbreadcrumb_elementtext(wd_handle)
        local_cirrus_album_release_date = Cirrus_Album_Metadata.get('albumReleaseDate')
        local_temp_cirrus_album_name = (global_cirrus_album_name[:32]+'...') if len(global_cirrus_album_name)>32 else global_cirrus_album_name
        if local_navigated_album == local_temp_cirrus_album_name:
            print "MSG:Validating Album('%s') in detail view!!!" %local_temp_cirrus_album_name
            local_ui_album_title = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_TITLE).text
            local_ui_artist_name = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_ARTIST_NAME).text
            print "Album Artist Name in detail view is %s" %local_ui_artist_name
            try:
                local_ui_album_release_date = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_RELEASE_DATE).text
                local_return_value = Validate_AlbumReleaseDate(local_ui_album_release_date, local_cirrus_album_release_date)
            except:
                print "Warning: No Album Release Date Found"
                pass
            
            local_ui_recommend_more = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_RECOMMEND_MORE).text

            if local_ui_recommend_more != 'Recommend more like this':
                local_return_value = False
            if local_ui_album_title == Cirrus_Album_Metadata.get('albumName'):
                print "MSG:Successfully validated the album name('%s') is same in both UI and CIRRUS for the album '%s' detail view" %(local_ui_album_title,local_ui_album_title)
            else:
                print "ERROR:The album name('%s') in CIRRUS and the album name ('%s') in UI detail view did not match" %(str(Cirrus_Album_Metadata.get('albumName')),local_ui_album_title)
                local_return_value = False
            try:
                local_ui_facebook_span = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_FB_SHARE)
                local_ui_facebook_span.is_displayed()
            except:
                print "Error: Could not find the Facebook share button in selected album view!!!"
                local_return_value = False
            try:
                local_ui_twitter_span = wd_handle.find_element_by_xpath(cirrus_constants.XPATH_ALBUM_TWITTER_SHARE)
                local_ui_twitter_span.is_displayed()
            except:
                print "Error: Could not find the twitter share button in selected album view!!!"
                local_return_value = False
        else:
            raise Exception("Error:Tried to Navigate to '%s' Album detail view, instead navigated to '%s' Album detail view" %(local_temp_cirrus_album_name,local_navigated_album))
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Set_AlbumDetail_AttributeValues(Cirrus_Album_Metadata):
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
        lib_ParserScript.global_param_str_attrkey_1 = 'albumName'
        lib_ParserScript.global_param_str_attrvalue_1=Cirrus_Album_Metadata.get('albumName')
        lib_ParserScript.global_param_str_attrkey_2= 'albumArtistName'
        lib_ParserScript.global_param_str_attrvalue_2=Cirrus_Album_Metadata.get('albumArtistName')
        lib_ParserScript.global_param_str_nextresultstoken =''
        return True
    except:
        return False
        
def Validate_AlbumPlay(wd_handle,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate if the album is playable
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
        local_xpath_play_sprite = global_album_xpath + cirrus_constants.XPATH_ALBUM_PLAY_SPRITE
        local_ui_track_play_sprite = wd_handle.find_element_by_xpath(local_xpath_play_sprite)
        local_ui_track_play_sprite.click()
        time.sleep(5)
        local_xpath_album_image = global_album_xpath + cirrus_constants.XPATH_ALBUM_IMAGE_1
        wd_handle.find_element_by_xpath(local_xpath_album_image).click()
        Set_AlbumDetail_AttributeValues(Cirrus_Album_Metadata)
        local_album_play_status = Validate_Track_DetailView(wd_handle,'Albums','', True)
        local_temp_album_name = Cirrus_Album_Metadata.get('albumName')
        if local_album_play_status:
            print "Successfully validated that the selected Album(%s) is playing" %local_temp_album_name
            return True
        else:
            print "Error: Could not play the selected Album(%s)" %local_temp_album_name
            return False
    except Exception as ex:
        print ex
        return False

def Download_Album_GridOptions(wd_handle,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate if the album is downloadable 
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
        local_element_ui_album_grid_option = wd_handle.find_element_by_xpath(global_album_xpath + cirrus_constants.XPATH_ALBUM_GRID)
        local_element_ui_album_grid_option.click()
        local_download_link = is_element_present(wd_handle, 'Download', 'LINKTEXT')
        if not local_download_link is False:
            local_download_link.click()
            print "MSG:Download link clicked Successfully!!!"
            local_return_value = True
        else:
            print "Error:Could not click the Download link!!!"
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
            
def Validate_TracksInAlbum(Obj_Element,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate the tracks in album is playable and has proper meta data
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
        local_cirrus_album_number_of_tracks = Cirrus_Album_Metadata.get('numTracks')
        local_element_ui_album_track_count = Obj_Element.find_element_by_xpath(global_album_xpath + cirrus_constants.XPATH_ALBUM_TRACKS_COUNT)
        local_ui_album_track_count = local_element_ui_album_track_count.text
        if local_cirrus_album_number_of_tracks >1:
            local_cirrus_tracks_count  = (str(local_cirrus_album_number_of_tracks)+ " items").strip()
        else:
            local_cirrus_tracks_count  = (str(local_cirrus_album_number_of_tracks)+ " item").strip()
        if (str(local_ui_album_track_count)).strip() == local_cirrus_tracks_count:
            print "MSG:Successfully validated the number of Tracks in Album(%s) is same in both UI and CIRRUS!!!" %local_ui_album_track_count
            local_return_value = True
        else:
            print "Error:Number of Tracks for Album in CIRRUS('%s') and Number of Tracks for Album in UI('%s') did not match!!!" %(local_cirrus_album_number_of_tracks,local_ui_album_track_count)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
        
def Validate_AlbumName(Obj_Element,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate if the album name matches
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
        global global_cirrus_album_name
        global_cirrus_album_name = Cirrus_Album_Metadata.get('albumName')
        local_element_ui_album_name = Obj_Element.find_element_by_xpath(global_album_xpath + cirrus_constants.XPATH_ALBUM_NAME)
        local_ui_album_name = local_element_ui_album_name.text
        if (str(local_ui_album_name)).strip() == (str(global_cirrus_album_name)).strip():
            print "MSG:Successfully validated the Album Name(%s) is same in both UI and CIRRUS!!!" %local_ui_album_name
            local_return_value = True
        else:
            print "Error:Album Name in CIRRUS('%s') and Album Name in UI('%s') did not match!!!" %(global_cirrus_album_name,local_ui_album_name)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
        
def Validate_AlbumArtistName(Obj_Element,Cirrus_Album_Metadata):
    """
    *********************************************************************
    Description     : This method will validate if the album artist name matches
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
        local_cirrus_album_artist_name = Cirrus_Album_Metadata.get('albumArtistName')
        local_element_ui_album_artist_name = Obj_Element.find_element_by_xpath(global_album_xpath + cirrus_constants.XPATH_ALBUM_ARTIST)
        local_ui_album_artist_name = local_element_ui_album_artist_name.text
        if (str(local_ui_album_artist_name)).strip() == (str(local_cirrus_album_artist_name)).strip():
            print "MSG:Successfully validated the Artist Name(%s) is same in both UI and CIRRUS!!!" %local_ui_album_artist_name
            local_return_value = True
        else:
            print "Error:Artist Name in CIRRUS('%s') and Artist Name in UI('%s') did not match!!!" %(local_cirrus_album_artist_name,local_ui_album_artist_name)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value