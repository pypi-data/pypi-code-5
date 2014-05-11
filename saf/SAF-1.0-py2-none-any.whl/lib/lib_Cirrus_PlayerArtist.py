'''
Created on Sep 20, 2013

@author: karthicm
'''
from lib_ParserScript import Generate_CirrusRequestUrl,get_ResultCount,HttpPost_CirrusRequestUrl,Return_Search_Dictionary,Set_CustomerId
import lib_ParserScript
import cirrus_constants
from lib_TestSetUp import wait_for_page_to_load
global global_endofartist_search_token, global_artist_token_count
global_endofartist_search_token = 0
global_artist_token_count = 0

def get_artistcount_from_cirrus(wd_handle,JsonRequestPath):
    """
    *********************************************************************
    Description     : This method will return the number of artist available in the customer library from CIRRUS
    Usage           : Used to validate the number of artist in the library with the UI data
    Return Value    : CIRRUS Artist count
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_artist_count = get_ResultCount(wd_handle,JsonRequestPath)
        return local_artist_count
    except Exception as ex:
        print ex
        return False

def Return_Artist_Dictionary(wd_handle,JsonRequestPath, Search_Item):
    """
    *********************************************************************
    Description     : This method will return the dictionary containing the meta data for the searched artist from the CIRRUS
    Usage           : Internal Module
    Return Value    : Searched Artist Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_request_url = Generate_CirrusRequestUrl(JsonRequestPath)
        local_search_status = lib_ParserScript.global_param_str_nextresultstoken
        if not local_search_status is None:
            local_response_dictionary =  HttpPost_CirrusRequestUrl(local_request_url)
            local_dictionary_artist_metadata = Return_Search_Dictionary(local_response_dictionary, Search_Item)
            return local_dictionary_artist_metadata
        return None
    except Exception as ex:
        print ex
        return False

def get_artistdetails_from_cirrus(wd_handle,JsonRequestPath,ArtistName=''):
    """
    *********************************************************************
    Description     : This method will search for the User artist from the entire CIRRUS library
    Usage           : Internal Module
    Return Value    : Searched Artist Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        Set_CustomerId(wd_handle)
        local_artist_metadata = Return_Artist_Dictionary(wd_handle,JsonRequestPath,ArtistName)
        if local_artist_metadata is None:
            return None 
        while not local_artist_metadata:
            ScrollBy_10Artist(wd_handle)
            local_artist_metadata = Return_Artist_Dictionary(wd_handle,JsonRequestPath,ArtistName)
        return local_artist_metadata
    except Exception as ex:
        print ex
        return False
    
def ScrollBy_10Artist(wd_handle):
    """
    *********************************************************************
    Description     : This method will scroll 10 artist at a time to identify the artist
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
        global global_endofartist_search_token
        if global_endofartist_search_token == local_temp_next_token: 
            global global_artist_token_count
            global_artist_token_count = global_artist_token_count+1
        if global_artist_token_count > 3:
            lib_ParserScript.global_param_str_nextresultstoken = None
        local_index = int(lib_ParserScript.global_param_str_nextresultstoken)-1
        local_xpath_artist_griditem = cirrus_constants.XPATH_ARTIST_GRID_1 + str(local_index)+ cirrus_constants.XPATH_ARTIST_GRID_2
        local_element_artist_griditem = wd_handle.find_element_by_xpath(local_xpath_artist_griditem)
        local_element_artist_griditem.location_once_scrolled_into_view
        wait_for_page_to_load(wd_handle)
        return True
    except Exception as ex:
        print ex
        return False