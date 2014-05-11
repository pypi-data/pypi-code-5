'''
Created on Aug 27, 2013

@author: karthicm
'''
import cirrus_constants
import lib_ParserScript
global global_endofsearch_token, global_token_count
global_endofsearch_token = 0
global_token_count = 0

def Return_Track_Dictionary(wd_handle,JsonRequestPath, Search_Item):
    """
    *********************************************************************
    Description     : This method will return the dictionary containing the meta data for the searched Track from the CIRRUS
    Usage           : Internal Module
    Return Value    : Searched Track Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_request_url = lib_ParserScript.Generate_CirrusRequestUrl(JsonRequestPath)
        local_search_status = lib_ParserScript.global_param_str_nextresultstoken
        if not local_search_status is None:
            local_response_dictionary =  lib_ParserScript.HttpPost_CirrusRequestUrl(local_request_url)
            local_dictionary_track_metadata = lib_ParserScript.Return_Search_Dictionary(local_response_dictionary, Search_Item)
            return local_dictionary_track_metadata
        return None
    except Exception as ex:
        print ex
        return False


def get_trackdetails_from_cirrus(wd_handle,JsonRequestPath,TrackName=''):
    """
    *********************************************************************
    Description     : This method will search for the User Track from the entire CIRRUS library
    Usage           : Internal Module
    Return Value    : Searched Track Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        lib_ParserScript.Set_CustomerId(wd_handle)
        local_track_metadata = Return_Track_Dictionary(wd_handle,JsonRequestPath,TrackName)
        if local_track_metadata is None:
            return None 
        while not local_track_metadata:
            ScrollBy_50Tracks(wd_handle)
            local_track_metadata = Return_Track_Dictionary(wd_handle,JsonRequestPath,TrackName)
            if local_track_metadata is None:
                break
        return local_track_metadata
    except Exception as ex:
        print ex
        return False

def ScrollBy_50Tracks(wd_handle):
    """
    *********************************************************************
    Description     : This method will scroll 50 Tracks at a time to identify the track
    Usage           : Internal Module
    Return Value    : True or False
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_temp_next_token =  lib_ParserScript.global_param_str_nextresultstoken
        if local_temp_next_token is None:
            return None
        global global_endofsearch_token
        if global_endofsearch_token == local_temp_next_token: 
            global global_token_count
            global_token_count = global_token_count+1
        if global_token_count > 3:
            lib_ParserScript.global_param_str_nextresultstoken = None
        local_index = int(local_temp_next_token)-1
        local_xpath_track_checkbox = cirrus_constants.XPATH_TRACK_CHECKBOX_1 +str(local_index)+ cirrus_constants.XPATH_TRACK_CHECKBOX_2
        local_element_track_checkbox = wd_handle.find_element_by_xpath(local_xpath_track_checkbox)
        local_element_track_checkbox.location_once_scrolled_into_view
        global_endofsearch_token = local_temp_next_token
        return True
    except Exception as ex:
        print ex
        return False
        
def get_songscount_from_cirrus(wd_handle,JsonRequestPath):
    """
    *********************************************************************
    Description     : This method will return the number of Tracks available in the customer library from CIRRUS
    Usage           : Used to validate the number of Tracks in the library with the UI data
    Return Value    : CIRRUS Genres count
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_tracks_count = lib_ParserScript.get_ResultCount(wd_handle,JsonRequestPath)
        return local_tracks_count
    except Exception as ex:
        print ex
        return False

        
        