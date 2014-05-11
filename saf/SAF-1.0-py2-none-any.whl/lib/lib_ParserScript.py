'''
Created on Aug 12, 2013

@author: karthicm
'''
import base64
import urllib2
import json
import cirrus_constants

global global_param_str_customerid
global global_param_str_attrkey_1 , global_param_str_attrkey_2
global global_param_str_attrvalue_1 , global_param_str_attrvalue_2
global global_param_str_nextresultstoken
global_param_str_nextresultstoken = ''
import codecs

def Generate_CirrusRequestUrl(Cirrus_FilePath):
    """
    *********************************************************************
    Description     : Generates the CIRRUS API Request URL from the JSON request file   
    Usage           : Internal Module
    Return Value    : Encoded Request URL
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/12/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_cirrusfile = codecs.open(Cirrus_FilePath,'r','utf-8')
        local_str_request_headers = local_cirrusfile.read()
        local_str_request_headers = Parse_JsonRequest(local_str_request_headers)
        local_encoded_request_headers = base64.b64encode(local_str_request_headers)
        local_request_url = cirrus_constants.CIRRUS_LIBRARY_URL + local_encoded_request_headers
        local_return_value = local_request_url
    except Exception as ex:
        print 'Exception error is: %s' % ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
        

def Get_CustomerId(wd_handle):
    """
    *********************************************************************
    Description     : Returns the Customer ID for the user from the Web browser  
    Usage           : Internal Module
    Return Value    : Customer ID of the Test Account
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/12/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_str_page_source = (wd_handle.page_source).encode('utf-8').strip()
        local_str_customerid =  local_str_page_source[local_str_page_source.find('"customerId":"')+len('"customerId":"'):local_str_page_source.find('","customerName":')]
        local_return_value = local_str_customerid
    except Exception as ex:
        print 'Exception error is: %s' % ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
            
    
def Set_CustomerId(wd_handle):
    """
    *********************************************************************
    Description     : Set the Customer ID for the user to the Parameter for parsing
    Usage           : Internal Module
    Return Value    : NA
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/12/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    global global_param_str_customerid
    global_param_str_customerid = Get_CustomerId(wd_handle)

def Parse_JsonRequest(Parameterized_JsonRequest):
    """
    *********************************************************************
    Description     : SAF defined parameters are identified by the syntax "((<parametername>))" and parsed with the runtime values for every request.
    Usage           : Internal Module
    Return Value    : Actual JSON request with real time values
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_bool_parameter_exist = False
        if '((' in Parameterized_JsonRequest:
            local_bool_parameter_exist = True
        while local_bool_parameter_exist:
            local_parameter =  Parameterized_JsonRequest[Parameterized_JsonRequest.find('((')+len('(('):Parameterized_JsonRequest.find('))')]
            local_runtime_parameter = '{'+local_parameter+'}'
            local_json_parameter = '(('+local_parameter+'))'
            Parameterized_JsonRequest = Parameterized_JsonRequest.replace(local_json_parameter,local_runtime_parameter.format(**globals()))
            if '((' not in Parameterized_JsonRequest:
                local_bool_parameter_exist = False
                local_actual_json_request = Parameterized_JsonRequest
        local_return_value = local_actual_json_request
    except Exception as ex:
        print 'Exception error is: %s' % ex
        local_return_value = False
        assert False
    finally:
        return local_return_value
    
def HttpPost_CirrusRequestUrl(Request_Url):
    """
    *********************************************************************
    Description     : Request URL is posted to the service and service response is read through for the required data.
    Usage           : Internal Module
    Return Value    : Response Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        local_service_response = urllib2.urlopen(Request_Url)
        local_temp_response_dictionary = local_service_response.read()
        local_response_dictionary = json.loads(local_temp_response_dictionary)
        Set_NextResultsToken(local_response_dictionary)
        local_return_value = local_response_dictionary
    except Exception as ex:
        print 'Cirrus Exception error is: %s' % ex
        local_return_value = False
        assert False
    finally:
        return local_return_value

                
def get_ResultCount(wd_handle,JsonRequestPath):
    """
    *********************************************************************
    Description     : Returns the total result count from the response dictionary
    Usage           : Internal Module
    Return Value    : Total result count
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
        local_request_url = Generate_CirrusRequestUrl(JsonRequestPath)
        local_response_dictionary =  HttpPost_CirrusRequestUrl(local_request_url)
        local_result_count = local_response_dictionary.get('resultCount')       
        return local_result_count
    except:
        return False

def Set_NextResultsToken(ResponseDictionary):
    """
    *********************************************************************
    Description     : This method will set the next result token value to retrieve the next set of data from the CIRRUS library.
    Usage           : Internal Module
    Return Value    : Next result count
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        if 'nextResultsToken' in ResponseDictionary.keys():
            local_nextresult_count = ResponseDictionary.get('nextResultsToken')
            global global_param_str_nextresultstoken
            if not local_nextresult_count == '': 
                global_param_str_nextresultstoken = local_nextresult_count
            elif 'playlist' in ResponseDictionary.keys():
                local_playlist_dictionary = ResponseDictionary.get('playlist')
                local_nextresult_count = local_playlist_dictionary.get('trackCount')
                if local_nextresult_count >50:
                    global_param_str_nextresultstoken = local_nextresult_count
                global_param_str_nextresultstoken = None
            return True
        else:
            return False
    except Exception as ex:
        print ex
        return False
    
def Return_Search_Dictionary(ResponseDictionary, Search_Item):
    """
    *********************************************************************
    Description     : This method will return the final dictionary containing the meta data of the searched item
    Usage           : Internal Module
    Return Value    : Search Item Dictionary
    ToDo            : NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :09/13/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    """
    try:
        if 'playlist' in ResponseDictionary.keys():
            local_playlist_dictionary = ResponseDictionary.get('playlist')
            local_tracks_array = local_playlist_dictionary.get('entryList')
        else:
            local_tracks_array = ResponseDictionary.get('selectItemList')
        local_dictionary_track_metadata = {}
        local_bool_found = False
        local_search_string = Search_Item.encode('UTF8')
        for DictItem in local_tracks_array:
            if local_bool_found == True:
                break
            for MetaData in DictItem.iteritems():
                local_dictionary_track_metadata = DictItem.get('metadata')                   
                Track_MetaData_Values = [x.encode('UTF8') for x in local_dictionary_track_metadata.values()]
                if not local_search_string =='':          
                    if local_search_string in Track_MetaData_Values:
                        local_bool_found = True
                        if 'numTracks' in DictItem.keys():
                            local_dictionary_track_metadata['numTracks'] = DictItem.get('numTracks')
                        return local_dictionary_track_metadata  #Return the Metadata of the searched track
                        break
                else:                          # Return the Metadata of First track
                    if 'numTracks' in DictItem.keys():
                        local_dictionary_track_metadata['numTracks'] = DictItem.get('numTracks') 
                    return local_dictionary_track_metadata
                    break
        return False
    except Exception as ex:
        print ex
        return False
