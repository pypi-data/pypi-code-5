'''
Created on Jan 24, 2013

@author: karthicm
'''
from lib_TestSetUp import is_element_present, wait_for_page_to_load
import lib_TestSetUp
import lib_Operations_Common

def click_link(wd_handle,Locator):
    '''
    *********************************************************************
    
    Keyword Name    :Click Link
    
    Usage           :Function Clicks on the Link with the given locator and  navigates to the referenced URL.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        local_element_link = Fnc_VerifyLinkElementExist(wd_handle, Locator)
        if not local_element_link is None:
            try:
                local_element_link.location_once_scrolled_into_view
                local_element_link.is_displayed()
            except:
                click_link(wd_handle, Locator)
            try:
                RefURL = Fnc_GetRefURL_Link(local_element_link)
                local_old_browserurl = wd_handle.current_url
                local_element_link.location_once_scrolled_into_view
                local_element_link.click()
                local_linkloaded  = Fnc_WaitforLinkToLoad(wd_handle, local_old_browserurl, RefURL)
                try:
                    local_numberofwindow_handles = len(wd_handle.window_handles)
                    if not local_numberofwindow_handles > 1:
                        try:
                            local_target_attrvalue = local_element_link.get_attribute('target')
                            if local_target_attrvalue == '_blank':
                                local_linkloaded = True
                        except:
                            pass
                        if not local_linkloaded:
                            raise Exception
                    else:
                        local_linkloaded = True
                    local_new_browserurl = wd_handle.current_url
                    if local_old_browserurl != local_new_browserurl:
                        print Locator, ' Link clicked Successfully and Browser navigated to "%s"' %local_new_browserurl
                    else:
                        #Element_Link.location_once_scrolled_into_view
                        #Element_Link.click()
                        print Locator, ' Link clicked Successfully!!!'
                    lib_TestSetUp.global_temp_element_locator = ''
                    return True
                except:
                    click_link(wd_handle, Locator)
            except Exception as ex:
                print 'Exception occurred -%s' % ex
                lib_TestSetUp.global_temp_element_locator = ''
                assert False
                return False
        else:
            lib_TestSetUp.global_temp_element_locator = ''
            assert False
            return False
    except:
        print "Error!!!Could not find the link element with the locator: " + Locator
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False

def Fnc_GetRefURL_Link(LinkElement):
    #Return True or False, Check if the Image link has ref
    try:
        if LinkElement is not False:
            local_refurl = str(LinkElement.get_attribute("href"))
            return local_refurl
        else:
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False  
    
def Fnc_WaitforLinkToLoad(wd_handle,CurrentBrowserURL, RefURL):
    try:
        # Verify if the page URL has the #RefURL
        local_ajax_load = lib_Operations_Common.wait_for_ajax_to_load(wd_handle)
        if not local_ajax_load and not ('#' in RefURL or "javascript" in RefURL):
            local_page_load_status = wait_for_page_to_load(wd_handle, CurrentBrowserURL)
            #LinkedElement = CheckElementPresent(wd_handle,"#tableContainer div.bodyContainer", "CSS")
            #if not "java" in RefURL and not '#' in RefURL:
            local_variable_type = type(local_page_load_status)
            if local_variable_type is bool:
                return local_page_load_status
            else:
                if RefURL in local_page_load_status:
                    return True
                elif local_page_load_status != CurrentBrowserURL:
                    return True
                else:
                    return False
            #else:
            #    return True # Return True if RefURL is contains Javascript or Jquery
        else:
            return True  
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
        
def Fnc_VerifyLinkElementExist(wd_handle, Link_Text,IsMultiple = False):
    try:
        #PARTIAL_LINKTEXT,LINKTEXT
        local_element_link = is_element_present(wd_handle, Link_Text)
        return local_element_link
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def Fnc_VerifyLinkElementsExist(wd_handle, Link_Text, IsMultiple = True):
    try:
        #PARTIAL_LINKTEXT,LINKTEXT
        local_element_links = is_element_present(wd_handle, Link_Text, 'LINKTEXT', IsMultiple)
        if local_element_links is False:
            local_element_links = is_element_present(wd_handle, Link_Text, 'PARTIAL_LINKTEXT', IsMultiple)
        if local_element_links is False:
            local_element_links = is_element_present(wd_handle,Link_Text)
        return local_element_links
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False