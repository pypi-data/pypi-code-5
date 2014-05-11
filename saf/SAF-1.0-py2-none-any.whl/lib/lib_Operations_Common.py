# -*- coding: utf-8 -*- 
'''
Created on Apr 22, 2013

@author: karthicm
'''
from selenium.webdriver.common.action_chains import ActionChains
import lib_TestSetUp
import datetime
import os
import lib_ProcessOutputFiles
import framework_constants
global global_old_wd_handle
from os.path import expanduser
from lxml.html import clean
import re

def return_datetimestring():
    try:
        local_today = datetime.datetime.today()
        local_string_today = str(local_today).split(' ')
        local_time = str(local_string_today[1]).split('.')
        local_string_today = local_string_today[0].replace('-', '')
        string_time = local_time[0].replace(':', '')
        local_string_date_time = local_string_today+ '_' +string_time
        return local_string_date_time
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
  
def return_datetimeformat(InputDateTime,Format= '%Y-%m-%dT%H:%M:%S.%fZ'):
    try:
        local_date_time = datetime.datetime.strptime(InputDateTime, Format)
        try:
            local_regular_date = datetime.datetime.strftime(local_date_time, "%b %d %Y")
            return local_regular_date
        except:
            print "Unable to get Regular date format. Check input: %s" % InputDateTime
            return False
    except Exception, err1:
        print "Invalid date provided.%s " % err1.message
        return False

def get_current_result_directory():
    try:
        local_today = datetime.date.today()
        local_string_today = str(local_today)
        local_string_today = local_string_today.replace('-', '')
        string_report_directory = "SAF_Reports_" +local_string_today
        local_user_directory = expanduser("~")
        if not os.path.exists(local_user_directory+"/"+string_report_directory):
            os.makedirs(local_user_directory+"/"+string_report_directory)
        local_result_directory =  local_user_directory+"/"+string_report_directory
        local_current_run_directory = lib_ProcessOutputFiles.CreateRunFolder(local_result_directory)
        return local_current_run_directory
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
    
def wait_for_ajax_to_load(wd_handle):
    try:
        try:
            local_jquery_execution_status = framework_constants.BROWSER_JQUERY_EXECUTION_COMMAND
            local_browserstate_value = wd_handle.execute_script(local_jquery_execution_status)
        except:
            local_jquery_execution_status = framework_constants.BROWSER_JQUERY_EXECUTION_UNDEFINED_COMMAND
            local_browserstate_value = wd_handle.execute_script(local_jquery_execution_status)
        local_bool_loading = False      
        while not local_browserstate_value == 0:
            local_bool_loading = True
            local_browserstate_value = wd_handle.execute_script(local_jquery_execution_status)
        if local_bool_loading:
            print "Loading frame.... "
        return local_bool_loading
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False   

def assert_element_present(wd_handle,ElementLocator):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        while local_element_under_test is not None:
            try:
                local_element_under_test.location_once_scrolled_into_view
                local_element_present = True
                lib_TestSetUp.global_temp_element_locator = ''
                return local_element_present
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        local_element_present = False
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
    except Exception as ex:
        if ex:
            print 'Exception Occurred, Could not find the element: %s' % ex
        local_element_present = False
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
    finally:
        return local_element_present
		
def mouse_hover(wd_handle,ElementLocator):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        while local_element_under_test is not None:
            try:
                local_hover = ActionChains(wd_handle).move_to_element(local_element_under_test)
                local_hover.perform()
                return True
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def assert_element_tooltip(wd_handle,ElementLocator,Expected_ToolTipValue):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        while local_element_under_test is not None:
            try:
                local_element_under_test.location_once_scrolled_into_view()
                mouse_hover(wd_handle, local_element_under_test)
                local_actual_tooltip_value = local_element_under_test.get_attribute('title')
                break
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        if local_actual_tooltip_value == Expected_ToolTipValue:
            print "MSG: Actual Tooltip value is '%s', and the  Expected Tooltip value is '%s'!" %(local_actual_tooltip_value,Expected_ToolTipValue)
            return True
        else:
            print "WARN: Actual Tooltip value is '%s', But Expected Tooltip value is '%s'!" %(local_actual_tooltip_value,Expected_ToolTipValue)
            return False
    except Exception as ex:
        if ex:
            print 'Exception occurred and error is: %s' % ex
        return False

def move_to_elementview(wd_handle,ElementLocator):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        while local_element_under_test is not None:
            try:
                local_element_under_test.location_once_scrolled_into_view
                return True
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle,ElementLocator)
        return False 
    except Exception as ex:
        if ex:
            print 'Exception occurred and error is: %s' % ex
        return False

def assert_text_present(wd_handle,ExpectedText):
    '''
    *********************************************************************
	
    Keyword Name    :Assert Text Present
	
    Usage           :Function will check if the particular text is present in the page and will return True or False based on the assertion.\n Function takes two arguments Webdriver_handle and Text to be searched for.
    
	ToDo            :NIL
    
	=====================================================================
    
	Created By          :Karthick Mani
    
	Created Date        :05/10/2013
    
	Last Modified By    :Karthick Mani
    
	Last Modified Date  :01/07/2014
    
	*********************************************************************
    '''
    try:
        local_pagesource = wd_handle.page_source
        if ExpectedText in local_pagesource:
        #if local_text_found:
            print "MSG: PASS, '%s' is present in the current page." %ExpectedText
            return True
        else:
            print "Warning!!! assert_text_present function returned False!!!, '%s' is not present in the current page." %ExpectedText
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
		
def ConvertToSeconds(Duration):
    '''
    *********************************************************************
    
	Keyword Name    : NA
    
	Usage           :Function Converts the time into seconds
    
	ToDo            :NIL
    =====================================================================
    
	Created By          :Karthick Mani
    
	Created Date        :05/10/2013
    
	Last Modified By    :Karthick Mani
    
	Last Modified Date  :06/18/2013
    
	*********************************************************************
    '''
    try:
        if ':' in str(Duration):
            local_array_time = str(Duration).split(':')
            local_integer_minute = int(local_array_time[0])
            local_integer_seconds = int(local_array_time[1])
            local_duration_in_seconds = int((local_integer_minute * 60) + local_integer_seconds)
            return local_duration_in_seconds
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False


def FloatEquals(FloatValue1,FloatValue2):
    '''
    *********************************************************************
    
	Keyword Name    :NA
    
	Usage           :Function checks if the two floats are equal
    
	ToDo            :NIL
    
	=====================================================================
    
	Created By          :Karthick Mani
    
	Created Date        :05/10/2013
    
	Last Modified By    :Karthick Mani
    
	Last Modified Date  :06/18/2013
    
	*********************************************************************
    '''
    try:
        if abs(FloatValue1-FloatValue2)< 0.000001:
            return 1
        else:
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def get_webelement_attribute(wd_handle,SAFElement,LinkedAttribute):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle, SAFElement)
        local_element_attribute_value = None
        while local_element_under_test is not None:
            try:
                local_element_attribute_value = local_element_under_test.get_attribute(LinkedAttribute)
                if not len(local_element_attribute_value)>0:
                    raise Exception
                return str(local_element_attribute_value)
                break
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle, SAFElement)
        return local_element_attribute_value
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def get_webelement_innerhtmltext(wd_handle, element):
    local_innerhtml = wd_handle.execute_script("return arguments[0].innerHTML", element)
    local_innertext_text = str(local_innerhtml).split("<")
    return local_innertext_text[0]

def get_webelement_text(wd_handle,SAFElement):
    try:
        local_element_under_test = lib_TestSetUp.is_element_present(wd_handle, SAFElement)
        local_target_element_text = None
        while local_element_under_test is not None:
            try:
                local_target_element_text = str(local_element_under_test.text)
                if not local_target_element_text:
                    local_target_element_text= get_webelement_innerhtmltext(wd_handle, local_element_under_test)
                return str(local_target_element_text).strip(' \t\n\r')
                break
            except:
                local_element_under_test = lib_TestSetUp.is_element_present(wd_handle, SAFElement)
        return local_target_element_text
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return None

def take_screenshot(wd_handle,ScreenshotFileName=''):
    try:
        #if 'ScreenshotFileName' in locals():
        if not ScreenshotFileName == '':
            local_screenshot_filename = "Screenshot_" + ScreenshotFileName
        else:
            local_datetime = return_datetimestring()
            local_screenshot_filename = "Screenshot_" + str(local_datetime)
        if not '.' in local_screenshot_filename:
            local_screenshot_name = str(local_screenshot_filename) + '.png'
        local_result_directory = get_current_result_directory()
        #ScreenshotDirectory = lib_TestSetUp.get_screenshot_directory()
        local_screenshot_directory = local_result_directory + "/screenshots"
        if not os.path.exists(local_screenshot_directory):
            os.makedirs(local_screenshot_directory)
            local_screenshot_path = local_screenshot_directory + '\\' + local_screenshot_name
        else:
            local_screenshot_path = local_screenshot_directory + '\\' + local_screenshot_name
        wd_handle.save_screenshot(local_screenshot_path)
        local_screenshot_path = os.path.abspath(local_screenshot_path)
        local_screenshot_path_array= local_screenshot_path.split('\\')
        local_screenshot_relativepath = local_screenshot_path_array[len(local_screenshot_path_array)-2]+'\\'+local_screenshot_path_array[len(local_screenshot_path_array)-1]
        return local_screenshot_relativepath
    except Exception as ex:
        print ex
        return False
            
def drag_and_drop(wd_handle, SourceElement,TargetElement):
    '''
    *********************************************************************
    
	Keyword Name    :Drag And Drop
    
	Usage           :Function takes three arguments, And drags the Target element to the Source Element destination
    
	ToDo            :NIL
    
	=====================================================================
    
	Created By          :Karthick Mani
    
	Created Date        :05/10/2013
    
	Last Modified By    :Karthick Mani
    
	Last Modified Date  :06/18/2013
    
	*********************************************************************
    '''
    try:
        local_source_element = lib_TestSetUp.is_element_present(wd_handle, SourceElement)
        local_target_element = lib_TestSetUp.is_element_present(wd_handle, TargetElement)
        ActionChains(wd_handle).drag_and_drop(local_source_element, local_target_element).perform()
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        print "\n!!!Error, Sorry could not drag and drop'"+ TargetElement+"' to '"+SourceElement +"'." 