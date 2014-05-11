'''
Created on Jan 24, 2013

@author: karthicm
'''
import lib_TestSetUp

def select_radio_button(wd_handle,RadioButtonLocator,RadioButtonLocatorType=None):
    '''
    *********************************************************************
    
    Keyword Name    :Click Button
    
    Usage           :Fuction will check if the button is present in the current page and will click on it. You can also check for the expected tooltip when hovering over the button.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        local_element_radiobutton = Fnc_VerifyButtonElementExist(wd_handle, RadioButtonLocator,RadioButtonLocatorType)
        try:
            while local_element_radiobutton is not None:
                try:
                    local_element_radiobutton.location_once_scrolled_into_view
                    local_element_radiobutton.click()
                    lib_TestSetUp.wait_for_page_to_load(wd_handle)
                    print "MSG: Successfully clicked the Button element with locator:'%s'!!!" %local_element_radiobutton
                    lib_TestSetUp.global_temp_element_locator = ''
                    local_is_radiobutton_selected = True
                    return local_is_radiobutton_selected
                except:
                    local_element_radiobutton = Fnc_VerifyButtonElementExist(wd_handle, RadioButtonLocator,RadioButtonLocatorType)             
            lib_TestSetUp.global_temp_element_locator = ''
            local_is_radiobutton_selected = False
            assert False
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
                BoolException = True
            print "Error!!!Could not find the Button element with the locator: '" + RadioButtonLocator +"'!!!"
            lib_TestSetUp.global_temp_element_locator = ''
            local_is_radiobutton_selected = False
            assert False
    except Exception as ex:
        if not BoolException:
            print 'Exception error is: %s' % ex
        lib_TestSetUp.global_temp_element_locator = ''
        local_is_radiobutton_selected = False
    finally:
        return local_is_radiobutton_selected


def Fnc_VerifyButtonElementExist(wd_handle, RadioButtonLocator, RadioButtonLocatorType):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        local_element_radiobutton = lib_TestSetUp.is_element_present(wd_handle,RadioButtonLocator,RadioButtonLocatorType)
        return local_element_radiobutton
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def is_radiobutton_checked(Obj_RadioButtonElement):
    try:
        if Obj_RadioButtonElement.is_selected():
            lib_TestSetUp.global_temp_element_locator = ''
            return True
        else:
            lib_TestSetUp.global_temp_element_locator = ''
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        lib_TestSetUp.global_temp_element_locator = ''
        return False
    