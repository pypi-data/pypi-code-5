#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib_TestSetUp import wait_for_page_to_load

def assert_browser_title(wd_handle,ExpectedBrowserTitle):
    '''
    *********************************************************************
    
    Keyword Name    :Assert Browser Title
    
    Usage           :Function will check the Browser title against the expected Title and will return True or False based on the assertion.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :02/11/2013
    
    *********************************************************************
    '''
    try:
        local_current_browser_title = (wd_handle.title).encode('utf-8')
        local_expected_browser_title = (ExpectedBrowserTitle).encode('utf-8')
        if local_current_browser_title == local_expected_browser_title:
            print "MSG: assert_browser_title function returned True!!!, Current Browser Title:'%s' & Expected Browser Title:'%s' matched for the current page." %(local_current_browser_title,local_expected_browser_title)
            local_browser_title_matched = True
        else:
            print "Warning!!! assert_browser_title function returned False!!!, Current Browser Title:'%s' & Expected Browser Title:'%s' did not match for the current page." %(local_current_browser_title,local_expected_browser_title)
            local_browser_title_matched = False
            assert False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        local_browser_title_matched = False
    finally:
        return local_browser_title_matched

def append_browser_url(wd_handle,urlappendstring):
    '''
    *********************************************************************
    
    Keyword Name    :Append Browser Url 
    
    Usage           :Function will append and navigate the current browser url with the given append string
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :12/12/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :12/12/2013
    
    *********************************************************************
    '''
    try:
        #if not '/' in urlappendstring:
        #    local_urlappend_string = '/'+urlappendstring
        local_current_browser_url = str(wd_handle.current_url)
        local_new_browser_url = local_current_browser_url + urlappendstring
        wd_handle.get(local_new_browser_url)
        wait_for_page_to_load(wd_handle, local_new_browser_url)
        print "MSG: browser_navigate function successfully navigated to the Given URL:'%s'!!!" %local_new_browser_url
        local_bool_browser_navigated = True
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        local_bool_browser_navigated = False
    finally:
        return local_bool_browser_navigated
    
def assert_url_contains_substring(wd_handle,Substring):
    '''
    *********************************************************************
    
    Keyword Name    :Assert Url Contains Substring
    
    Usage           :Function will check the existance of the Substring in the browser URL and will return True or False based on the assertion.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :12/11/2013
    
    *********************************************************************
    '''
    try:
        local_current_browser_url = str(wd_handle.current_url)
        if Substring in local_current_browser_url:
            print "MSG: assert_url_contains_substring function returned True!!!, Substring:'%s' found in the current browser URL." % Substring
            local_bool_substring_found = True
        else:
            print "Warning!!! assert_url_contains_substring function returned False!!!, Substring:'%s' not found in the current browser URL." % Substring
            local_bool_substring_found = False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        local_bool_substring_found = False
    finally:
        return local_bool_substring_found

def return_substring_from_browserurl(wd_handle,LeftString,RightString):
    '''
    *********************************************************************
    
    Keyword Name    :Return Substring From Browserurl
    
    Usage           :Function returns the substring between the given left and right strings in the current browser URL.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        local_current_browser_url = str(wd_handle.current_url)
        print local_current_browser_url
        if (LeftString in local_current_browser_url) and (RightString in local_current_browser_url):
            local_substring_in_current_url =  local_current_browser_url[local_current_browser_url.find(LeftString)+len(LeftString):local_current_browser_url.find(RightString)]
            print "MSG: return_substring_from_browserurl function returned the substring:'%s' !!!" %local_substring_in_current_url
            return local_substring_in_current_url
        else:
            print "Error!!!, Left string :'%s' Or right string:'%s' is not present in the Current Browser URL" %(LeftString,RightString)
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def navigate_browser(wd_handle,New_URL):
    '''
    *********************************************************************
    
    Keyword Name    :Browser Navigate
    
    Usage           :Function navigates the current browser to the given URL
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        wd_handle.get(New_URL)
        wait_for_page_to_load(wd_handle, New_URL)
        print "MSG: browser_navigate function successfully navigated to the Given URL:'%s'!!!" %New_URL
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
           
def navigate_browser_back(wd_handle):
    try:
        wd_handle.back()
        return True
    except Exception as ex:
        if ex:
            print 'Error: Browser could not navigate back in the history!!!'
            print 'Exception error is: %s' % ex
        return False
    
def navigate_browser_forward(wd_handle):
    try:
        wd_handle.forward()
        return True
    except Exception as ex:
        if ex:
            print 'Error: Browser could not navigate forward in the history!!!'
            print 'Exception error is: %s' % ex
        return False

def delete_all_cookies(wd_handle):
    try:
        wd_handle.delete_all_cookies
        switch_window(wd_handle, 'clear')
        print "Cleared all browser cookies"
        return True
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

    
def switch_window(wd_handle, Window = 'NEW'):
    '''
    *********************************************************************
    
    Keyword Name    :Switch Window
    
    Usage           :Switches between two browser windows, To switch to a new Browser window always use "switch_window(wd_handle,'NEW')".\nTo get back to the parent browser use switch_window(wd_handle)
    
    ToDo            :Support switching for more than two browser windows.
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        try:
            global global_old_wd_handle
            if Window == 'clear':
                global_old_wd_handle = None
                return True
            global_old_wd_handle
            pass
        except:
            print "Old Window Handle Set to None"
            global_old_wd_handle = None
        if global_old_wd_handle is None:
            global_old_wd_handle = wd_handle.current_window_handle
            print "Old Window Handle Set to Driver handle"
            print "Old Window Handle is : %s" % global_old_wd_handle
        #if Window.upper() is 'NEW':
            local_new_wd_handle = wd_handle.window_handles[-1]
            print "New Window Handle is : %s" % local_new_wd_handle
            wd_handle = wd_handle.switch_to_window(local_new_wd_handle)
            wait_for_page_to_load(wd_handle)
            #print "Current Window Handle after switching is : %s" % wd_handle
            print "MSG: switch_window function successfully switched handler to the new browser window"
        else:
            wd_handle = wd_handle.switch_to_window(global_old_wd_handle)
            wait_for_page_to_load(wd_handle)
            global_old_wd_handle=None
            print "MSG: switch_window function successfully switched back handler to the parent browser window"
        return wd_handle
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False