'''
Created on Jan 24, 2013

@author: karthicm
'''
import lib_TestSetUp
    
def click_button(wd_handle,ButtonLocator,Expected_ToolTipValue = None ):
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
        ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        while ButtonElement is not None:
            try:
                if not Expected_ToolTipValue is None:
                    Fnc_VerifyButtonToolTip(ButtonElement, Expected_ToolTipValue)
                ButtonElement.location_once_scrolled_into_view
                ButtonElement.click()
                lib_TestSetUp.wait_for_page_to_load(wd_handle)
                print "MSG: Successfully clicked the Button element with locator:'%s'!!!" %ButtonLocator
                lib_TestSetUp.TempElementLocator = ''
                lib_TestSetUp.global_temp_element_locator = ''
                return True
            except:
                ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except Exception as ex:
        print "Error!!!Could not find the Button element with the locator: '%s'!!!" %ButtonLocator
        print "Exception is:%s" % ex
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False

def is_button_enabled(wd_handle, ButtonLocator):
    try:
        ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        while ButtonElement is not None:
            try:
                Bln_IsEnabled = ButtonElement.is_enabled()
                lib_TestSetUp.TempElementLocator = ''
                lib_TestSetUp.global_temp_element_locator = ''
                return Bln_IsEnabled
            except:
                ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except:
        print "Error!!!Could not find the Button element with the locator: '%s'!!!" %ButtonLocator
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False

def Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        Button = lib_TestSetUp.is_element_present(wd_handle,ButtonLocator)
        return Button
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

'''
#Why will you have multiple buttons with same name? or locator?
def Fnc_VerifyButtonElementsExist(wd_handle, ButtonLocator, IsMultiple = True):
    try:
        Button = is_element_present(wd_handle, ButtonLocator, IsMultiple)
        return Button
    except:
        return False
'''
    
def Fnc_VerifyButtonToolTip(Button, Expected_ToolTipValue):
    #Verify ToolTip by the element title
    try:
        Actual_ToolTipValue = Fnc_CheckIfToolTipExists(Button)
        try:
            if Actual_ToolTipValue == Expected_ToolTipValue:
                print "MSG: Actual Tooltip value is '%s', and the  Expected Tooltip value is '%s'!" %(Actual_ToolTipValue,Expected_ToolTipValue)
                pass
            else:
                print "WARN: Actual Tooltip value is '%s', But Expected Tooltip value is '%s'!" %(Actual_ToolTipValue,Expected_ToolTipValue)
        except:
            print "MSG: Tooltip does not exist for '%s' button" % str(Button)
        return True
    except:
        return False
   
def Fnc_CheckIfToolTipExists(Button):
    try:
        ToolTip = Button.get_attribute('title')
        if ToolTip:
            return ToolTip
        else:
            return False
        return ToolTip
    except:
        return False

def assert_button_name(wd_handle,ButtonLocator,ExpectedButtonName):
    try:
        ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        while ButtonElement is not None:
            try:
                try:
                    ActualButtonName = ButtonElement.get_attribute('value')
                    if ActualButtonName is None:
                        assert False
                    if ActualButtonName == ExpectedButtonName:
                        print "'%s' button has the same name as expected!!!" %ActualButtonName
                        lib_TestSetUp.TempElementLocator = ''
                        lib_TestSetUp.global_temp_element_locator = ''
                        return True
                    else:
                        print "'%s' button's expected name is '%s'!!!" %(ActualButtonName, ExpectedButtonName)
                        lib_TestSetUp.TempElementLocator = ''
                        lib_TestSetUp.global_temp_element_locator = ''
                        return False
                except:
                    pass
                ActualButtonName = ButtonElement.text
                if ActualButtonName == ExpectedButtonName:
                    print "'%s' button has the same name as expected!!!" %ActualButtonName
                    lib_TestSetUp.TempElementLocator = ''
                    lib_TestSetUp.global_temp_element_locator = ''
                    return True
                else:
                    print "'%s' button's expected name is '%s'!!!" %(ActualButtonName, ExpectedButtonName)
                    lib_TestSetUp.TempElementLocator = ''
                    lib_TestSetUp.global_temp_element_locator = ''
                    return False
            except:
                ButtonElement = Fnc_VerifyButtonElementExist(wd_handle, ButtonLocator)
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        assert False
        return False
    except Exception as ex:
        lib_TestSetUp.TempElementLocator = ''
        lib_TestSetUp.global_temp_element_locator = ''
        print ex
        return False
