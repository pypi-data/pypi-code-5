'''
Created on Jan 24, 2013

@author: karthicm
'''
import lib_TestSetUp

def select_checkbox(wd_handle,CheckBoxLocator):
    '''
    *********************************************************************
    
	Keyword Name    :Select Checkbox
    
	Usage           :Function will select the checkbox in the current page with the given locator
	
	Return Value    : Returns True is selected else Returns False  
    
	ToDo            :NIL
    
	=====================================================================
    
	Created By          :Karthick Mani
    
	Created Date        :05/10/2013
    
	Last Modified By    :Karthick Mani
    
	Last Modified Date  :06/18/2013
    
	*********************************************************************
    '''
    try:
        Element_CheckBox = Fnc_VerifyCheckBoxElementExist(wd_handle, CheckBoxLocator)
        while Element_CheckBox is not None:
            try:
                Element_CheckBox.location_once_scrolled_into_view
                Element_CheckBox.click()
                lib_TestSetUp.wait_for_page_to_load(wd_handle)
                print "MSG: Successfully selected the checkbox element with locator:'%s'!!!" %CheckBoxLocator
                lib_TestSetUp.global_temp_element_locator = ''
                return True
                break
            except:
                Element_CheckBox = Fnc_VerifyCheckBoxElementExist(wd_handle, CheckBoxLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except:
        print "Error!!!Could not find the CheckBox element with the locator: '%s'!!!" %CheckBoxLocator
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False

def is_checkbox_selected(wd_handle,CheckBoxLocator):
    '''
    *********************************************************************
    
    Keyword Name    :Is Checkbox Selected
    
    Usage           :Function will check if the checkbox is selected or not
    
    Return Value    :Returns True is selected else Returns False  
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :08/12/2013
    
    *********************************************************************
    '''
    try:
        Element_CheckBox = Fnc_VerifyCheckBoxElementExist(wd_handle, CheckBoxLocator)
        while Element_CheckBox is not None:
            try:
                if Element_CheckBox.is_selected():
                    lib_TestSetUp.global_temp_element_locator = ''
                    return True
                else:
                    lib_TestSetUp.global_temp_element_locator = ''
                    return False
            except:
                Element_CheckBox = Fnc_VerifyCheckBoxElementExist(wd_handle, CheckBoxLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        lib_TestSetUp.global_temp_element_locator = ''
        return False
    
def SelectAutoRipCheckBox(wd_handle):
    AutoRip = wd_handle.find_element_by_css_selector('img[alt="AutoRip"]')
    AutoRip.click()
    lib_TestSetUp.wait_for_page_to_load(wd_handle)
    
def Fnc_VerifyCheckBoxElementExist(wd_handle, CheckBoxLocator):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        CheckBox = lib_TestSetUp.is_element_present(wd_handle,CheckBoxLocator)
        return CheckBox
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False
