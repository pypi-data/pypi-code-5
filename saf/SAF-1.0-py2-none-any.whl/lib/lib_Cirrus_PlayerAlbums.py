'''
Created on Aug 29, 2013
@author: karthicm
'''
import lib_ParserScript
import cirrus_constants
from lib_TestSetUp import wait_for_page_to_load
global global_endofalbum_search_token, global_album_token_count
global_endofalbum_search_token = 0
global_album_token_count = 0

def get_albumcount_from_cirrus(wd_handle,JsonRequestPath):
    """
    *********************************************************************
    Description     : This method will return the number of albums available in the customer library from CIRRUS
    Usage           : Used to validate the number of album in the library with the UI data
    Return Value    : CIRRUS Album count
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_album_count = lib_ParserScript.get_ResultCount(wd_handle,JsonRequestPath)
        return local_album_count
    except Exception as ex:
        print ex
        return False

def Return_Album_Dictionary(wd_handle,JsonRequestPath, Search_Item):
    """
    *********************************************************************
    Description     : This method will return the dictionary containing the meta data for the searched album from the CIRRUS
    Usage           : Internal Module
    Return Value    : Searched Album Dictionary
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
            local_dictionary_album_metadata = lib_ParserScript.Return_Search_Dictionary(local_response_dictionary, Search_Item)
            return local_dictionary_album_metadata
        return None
    except Exception as ex:
        print ex
        return False

def get_albumdetails_from_cirrus(wd_handle,JsonRequestPath,AlbumName=''):
    """
    *********************************************************************
    Description     : This method will search for the User album from the entire CIRRUS library
    Usage           : Internal Module
    Return Value    : Searched Album Dictionary
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
        local_album_metadata = Return_Album_Dictionary(wd_handle,JsonRequestPath,AlbumName)
        if local_album_metadata is None:
            return None 
        while not local_album_metadata:
            ScrollBy_10Albums(wd_handle)
            local_album_metadata = Return_Album_Dictionary(wd_handle,JsonRequestPath,AlbumName)
        return local_album_metadata
    except Exception as ex:
        print ex
        return False
    
def ScrollBy_10Albums(wd_handle): 
    """
    *********************************************************************
    Description     : This method will scroll 10 albums at a time to identify the album
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
        wait_for_page_to_load(wd_handle)
        local_temp_next_token =  lib_ParserScript.global_param_str_nextresultstoken
        if local_temp_next_token is None:
            return None
        global global_endofalbum_search_token
        if global_endofalbum_search_token == local_temp_next_token: 
            global global_album_token_count
            global_album_token_count = global_album_token_count+1
        if global_album_token_count > 3:
            lib_ParserScript.global_param_str_nextresultstoken = None
        local_index = int(lib_ParserScript.global_param_str_nextresultstoken)-1
        local_xpath_album_griditem = cirrus_constants.XPATH_ALBUM_GRID_1 +str(local_index)+cirrus_constants.XPATH_ALBUM_GRID_2
        local_element_album_griditem = wd_handle.find_element_by_xpath(local_xpath_album_griditem)
        local_element_album_griditem.location_once_scrolled_into_view
        wait_for_page_to_load(wd_handle)
        return True
    except Exception as ex:
        print ex
        return False