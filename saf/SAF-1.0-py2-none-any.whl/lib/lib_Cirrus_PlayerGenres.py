'''
Created on Sep 20, 2013

@author: karthicm
'''

import lib_ParserScript
import cirrus_constants
from lib_TestSetUp import wait_for_page_to_load
global global_endofgenres_search_token, global_genres_token_count
global_endofgenres_search_token = 0
global_genres_token_count = 0

def get_genrescount_from_cirrus(wd_handle,JsonRequestPath):
    """
    *********************************************************************
    Description     : This method will return the number of genres available in the customer library from CIRRUS
    Usage           : Used to validate the number of genres in the library with the UI data
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
        local_genres_count = lib_ParserScript.get_ResultCount(wd_handle,JsonRequestPath)
        return local_genres_count
    except Exception as ex:
        print ex
        return False

def Return_Genres_Dictionary(wd_handle,JsonRequestPath, Search_Item):
    """
    *********************************************************************
    Description     : This method will return the dictionary containing the meta data for the searched Genres from the CIRRUS
    Usage           : Internal Module
    Return Value    : Searched Genres Dictionary
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
            local_dictionary_genres_metadata = lib_ParserScript.Return_Search_Dictionary(local_response_dictionary, Search_Item)
            return local_dictionary_genres_metadata
        return None
    except Exception as ex:
        print ex
        return False

def get_genresdetails_from_cirrus(wd_handle,JsonRequestPath,GenresName=''):
    """
    *********************************************************************
    Description     : This method will search for the User Genres from the entire CIRRUS library
    Usage           : Internal Module
    Return Value    : Searched Genres Dictionary
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
        local_genres_metadata = Return_Genres_Dictionary(wd_handle,JsonRequestPath,GenresName)
        if local_genres_metadata is None:
            return None 
        while not local_genres_metadata:
            ScrollBy_10Genres(wd_handle)
            local_genres_metadata = Return_Genres_Dictionary(wd_handle,JsonRequestPath,GenresName)
        return local_genres_metadata
    except Exception as ex:
        print ex
        return False
    
def ScrollBy_10Genres(wd_handle):
    """
    *********************************************************************
    Description     : This method will scroll 10 Genres at a time to identify the genres
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
        global global_endofgenres_search_token
        if global_endofgenres_search_token == local_temp_next_token: 
            global global_genres_token_count
            global_genres_token_count = global_genres_token_count+1
        if global_genres_token_count > 3:
            lib_ParserScript.global_param_str_nextresultstoken = None
        local_index = int(lib_ParserScript.global_param_str_nextresultstoken)-1
        local_xpath_genres_griditem = cirrus_constants.XPATH_GENRES_GRID_1 + str(local_index) + cirrus_constants.XPATH_GENRES_GRID_2
        local_element_genres_griditem = wd_handle.find_element_by_xpath(local_xpath_genres_griditem)
        local_element_genres_griditem.location_once_scrolled_into_view
        wait_for_page_to_load(wd_handle)
        return True
    except Exception as ex:
        print ex
        return False