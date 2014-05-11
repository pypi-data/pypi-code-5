'''
Created on Sep 20, 2013

@author: karthicm
'''
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
import cirrus_constants
import lib_ParserScript
from Module_Songs import get_lastbreadcrumb_elementtext,Validate_Track_DetailView
from lib_Cirrus_PlayerGenres import get_genrescount_from_cirrus,get_genresdetails_from_cirrus


global global_genres_xpath

def validate_genres_count(wd_handle,UIGenresCount):
    '''
    *********************************************************************
    
    Keyword Name    :Validate Genres Count
    
    Usage           :Function validates the total Genres count returned by CIRRUS service Vs the total Genres Count in the Player for the customer. Example: "Validate Genres Count (wd_handle,25)"
    
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
        local_cirrus_genres_count = get_genrescount_from_cirrus(wd_handle, cirrus_constants.CIRRUS_API_GENRES_COUNT_REQUEST_FILE)
        if int(UIGenresCount) == local_cirrus_genres_count:
            print "MSG:Successfully Verified Genres count is '%s' in both CIRRUS and UI!!!" % str(local_cirrus_genres_count)
            local_return_value = True
        else:
            print "Error:Genres count in CIRRUS('%s') and the Genres count in UI ('%s') did not match!!!" %(str(local_cirrus_genres_count),str(UIGenresCount))
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    


def play_validate_genres_view(wd_handle,GenresName = ''):
    '''
    *********************************************************************
    
    Keyword Name    :Play Validate Genres View
    
    Usage           :Function will validate the Genres 'Title','Album','Artist' and 'Time' against the CIRRUS response for the given GenresName in Songs View.
                     If GenresName is not specified, will validate the first Genres by default. 
    
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
        if local_last_breadcrumb_text == 'Genres':
            print "Validating Genres in %s view" %local_last_breadcrumb_text
            lib_ParserScript.global_param_str_nextresultstoken = ''
            local_genres_meta_data = get_genresdetails_from_cirrus(wd_handle,cirrus_constants.CIRRUS_API_ALL_GENRES_REQUEST_FILE,GenresName)
            if not local_genres_meta_data is None:
                local_return_value = play_validate_genres(wd_handle, local_genres_meta_data)
                lib_ParserScript.global_param_str_nextresultstoken = ''
            else:
                raise Exception("Error:Selected Genres('%s') does not exist in the '%s' view." %(GenresName, local_last_breadcrumb_text))
                local_return_value = False
        else:
            raise Exception('Error: Wrong view selected, Please navigate to Genres view to use "Play Validate Genres View" Keyword, or prefer using keyword for %s' %local_last_breadcrumb_text)
            local_return_value = False
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def play_validate_genres(wd_handle,Genres_MetaData):
    """
    *********************************************************************
    Description     : This method will validate the genres and its details view.
    Usage           : Internal module used to validate the metadata, numnber of tracks in genres etc
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
        local_cirrus_genres_name = Genres_MetaData.get('primaryGenre')
        global global_genres_xpath
        global_genres_xpath = cirrus_constants.XPATH_GENRES_1 + str(local_cirrus_genres_name) + cirrus_constants.XPATH_GENRES_2
        try:
            Genres_Element = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(global_genres_xpath))
        except:
            local_return_value = False
            raise NoSuchElementException
        #Validate_GenresName(Genres_Element, Genres_MetaData)
        #Validate_AlbumGenresName(Album_Element, Genres_MetaData)
        local_is_tracks_in_genres_verified = Validate_TracksInGenres(Genres_Element, Genres_MetaData)
        local_is_genres_play_verified = Validate_GenresPlay(wd_handle, Genres_MetaData)
        if local_is_tracks_in_genres_verified and local_is_genres_play_verified:
            local_return_value = True
        else:
            local_return_value = False
        #Validate_GenresDetailView(wd_handle, Genres_MetaData)
    except Exception as ex:
        if not ex =="":
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Validate_TracksInGenres(Obj_Element,Genres_MetaData):
    """
    *********************************************************************
    Description     : This method will validate the tracks in genres is playable and has proper meta data
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
        local_cirrus_genres_number_of_tracks = Genres_MetaData.get('numTracks')
        local_element_ui_genres_tracks_count = Obj_Element.find_element_by_xpath(global_genres_xpath + cirrus_constants.XPATH_GENRES_TRACK_COUNT)
        local_ui_genres_tracks_count = local_element_ui_genres_tracks_count.text
        if local_cirrus_genres_number_of_tracks >1:
            local_cirrus_genres_tracks_count  = (str(local_cirrus_genres_number_of_tracks)+ " items").strip()
        else:
            local_cirrus_genres_tracks_count  = (str(local_cirrus_genres_number_of_tracks)+ " item").strip()
        local_temp_genres_name = Genres_MetaData.get('primaryGenre')
        if (str(local_ui_genres_tracks_count)).strip() == local_cirrus_genres_tracks_count:
            print "MSG:Successfully validated the number of Tracks('%s') in selected Genres('%s') is same in both UI and CIRRUS!!!" %(local_ui_genres_tracks_count,local_temp_genres_name)
            local_return_value = True
        else:
            print "Error:Number of Tracks in CIRRUS('%s') and Number of Tracks in UI('%s') did not match for Genres('%s')!!!" %(local_cirrus_genres_number_of_tracks,local_ui_genres_tracks_count,local_temp_genres_name)
            local_return_value = False
    except Exception as ex:
        if ex:
            print "Exception Occurred %s" %ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

def Set_GenresDetail_AttributeValues(Genres_MetaData):
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
        lib_ParserScript.global_param_str_attrkey_1 = 'primaryGenre'
        lib_ParserScript.global_param_str_attrvalue_1=Genres_MetaData.get('primaryGenre')
        lib_ParserScript.global_param_str_nextresultstoken =''
        return True
    except:
        return False
    
def Validate_GenresPlay(wd_handle,Genres_MetaData):
    """
    *********************************************************************
    Description     : This method will validate if the genres is playable
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
        local_xpath_play_sprite = global_genres_xpath + cirrus_constants.XPATH_GENRES_PLAY_SPRITE
        local_ui_track_play_sprite = wd_handle.find_element_by_xpath(local_xpath_play_sprite)
        local_ui_track_play_sprite.click()
        time.sleep(5)
        local_xpath_genres_image = global_genres_xpath + cirrus_constants.XPATH_GENRES_IMAGE
        wd_handle.find_element_by_xpath(local_xpath_genres_image).click()
        Set_GenresDetail_AttributeValues(Genres_MetaData)
        local_genres_track_play_status = Validate_Track_DetailView(wd_handle,'Genres','', True)
        local_temp_genres_name = Genres_MetaData.get('primaryGenre')
        if local_genres_track_play_status:
            print "Successfully validated that the selected Genres(%s) is playing" %local_temp_genres_name
            return True
        else:
            print "Error: Could not play the selected Genres(%s)" %local_temp_genres_name
            return False
    except Exception as ex:
        print ex
        return False