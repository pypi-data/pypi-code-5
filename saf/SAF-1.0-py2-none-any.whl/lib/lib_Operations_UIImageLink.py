'''
Created on Jan 24, 2013

@author: karthicm
'''
import lib_TestSetUp

def click_image_link(wd_handle,Locator):
    '''
    *********************************************************************
    
    Keyword Name    :Click Image Link
    
    Usage           :Function clicks on an Image link and navigates the browsers to referenced URL
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        local_element_imagelink = Fnc_VerifyImageLinkElementExist(wd_handle, Locator)
        if not local_element_imagelink is None:
            try:
                local_element_imagelink.location_once_scrolled_into_view
                local_element_imagelink.is_displayed()
            except:
                click_image_link(wd_handle,Locator)
            try:
                local_refurl = Fnc_GetRefURL_ImageLink(local_element_imagelink)
                local_old_browserurl = wd_handle.current_url
                local_element_imagelink.location_once_scrolled_into_view
                local_element_imagelink.click()
                local_linkloaded = Fnc_WaitforImageLinkToLoad(wd_handle, local_old_browserurl, local_refurl)
                try:
                    if not local_linkloaded:
                        raise Exception
                    local_new_browserurl = wd_handle.current_url
                    if local_old_browserurl != local_new_browserurl:
                        print Locator, ' Link clicked Successfully and Browser navigated to "%s"' %local_new_browserurl
                    else:
                        print Locator, ' Link clicked Successfully!!!'
                    lib_TestSetUp.global_temp_element_locator = ''
                    local_is_imageclicked =  True
                except:
                    click_image_link(wd_handle, Locator)
            except Exception as ex:
                print 'Exception error is: %s' % ex
                lib_TestSetUp.global_temp_element_locator = ''
                local_is_imageclicked = False
                assert False
        else:
            lib_TestSetUp.global_temp_element_locator = ''
            local_is_imageclicked = False
            assert False
    except:
        print "Error!!!Could not find the ImageLink element with the locator: " + Locator
        lib_TestSetUp.global_temp_element_locator = ''
        local_is_imageclicked = False
        assert False
    finally:
        return local_is_imageclicked

def Fnc_GetRefURL_ImageLink(LinkElement):
    #Return True or False, Check if the Image link has ref
    try:
        if LinkElement is not False:
            local_refurl = str(LinkElement.get_attribute("href"))
            return local_refurl
        else:
            return False
    except:
        return False  
    
def Fnc_WaitforImageLinkToLoad(wd_handle,CurrentBrowserURL, RefURL):
    try:
        # Verify if the page URL has the #RefURL
        local_page_load_status = lib_TestSetUp.wait_for_page_to_load(wd_handle, CurrentBrowserURL)
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
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
        
def Fnc_VerifyImageLinkElementExist(wd_handle, Link_Text, IsMultiple = False):
    try:
        #PARTIAL_LINKTEXT,LINKTEXT
        local_imagelink = lib_TestSetUp.is_element_present(wd_handle, Link_Text)
        return local_imagelink
    except:
        return False

def Fnc_VerifyImageLinkElementsExist(wd_handle, Link_Text, IsMultiple = True):
    try:
        #PARTIAL_LINKTEXT,LINKTEXT
        local_imagelinks = lib_TestSetUp.is_element_present(wd_handle, Link_Text, 'LINKTEXT', IsMultiple)
        if local_imagelinks is False:
            local_imagelinks = lib_TestSetUp.is_element_present(wd_handle, Link_Text, 'PARTIAL_LINKTEXT', IsMultiple)
        return local_imagelinks
    except:
        return False    
    