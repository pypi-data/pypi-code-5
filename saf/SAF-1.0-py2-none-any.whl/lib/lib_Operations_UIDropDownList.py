'''
Created on Jan 24, 2013

@author: karthicm
'''
from selenium.webdriver.support.ui import Select
import lib_TestSetUp


def select_from_dropdown(wd_handle,DropDownLocator,DropDownText):
    '''
    *********************************************************************
    Keyword Name    :Select From Dropdown
    Usage           :Functions selects the text in the dropdown list using the given dropdown locator and text
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :01/07/2014
    *********************************************************************
    '''
    try:
        local_bool_exception = False
        local_element_dropdown = Fnc_VerifyDropDownElementExist(wd_handle, DropDownLocator)
        while local_element_dropdown is not None:
            if local_element_dropdown is not False:
                try:
                    Select(local_element_dropdown).select_by_visible_text(DropDownText)
                    print "MSG:Successfully selected the text %s from the DropDown Menu %s" % (DropDownText , DropDownLocator)
                    lib_TestSetUp.global_temp_element_locator = ''
                    return True
                except:
                    print "Error!!!: Could not find dropdown text:'%s' in the DropDown list!!!" %DropDownText
                    local_bool_exception = True
                    lib_TestSetUp.global_temp_element_locator = ''
                    assert False
                    return False
            else:
                local_element_dropdown = Fnc_VerifyDropDownElementExist(wd_handle, DropDownLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except Exception as ex:
        if not local_bool_exception:
            print 'Exception error is: %s' % ex
            assert False
        if not local_element_dropdown:
            print "Error!!!Could not find the Button element with the locator: " + DropDownLocator
            assert False
        lib_TestSetUp.global_temp_element_locator = ''
        return False
		
def Fnc_VerifyDropDownElementExist(wd_handle,DropDownLocator):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        local_element_dropdown = lib_TestSetUp.is_element_present(wd_handle,DropDownLocator)
        return local_element_dropdown
    except:
        return False
    
