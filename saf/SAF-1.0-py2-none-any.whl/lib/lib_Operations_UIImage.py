'''
Created on Jan 24, 2013

@author: karthicm
'''
from robot.utils.asserts import assert_true
import lib_TestSetUp
    
def click_image(wd_handle,ButtonLocator):
    '''
    *********************************************************************
    
    Keyword Name    :Click Image
    
    Usage           :Fuction will check if the Image is present in the current page and will click on it.
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        local_image_element = Fnc_VerifyImageElementExist(wd_handle, ButtonLocator)
        while local_image_element is not None:
            try:
                local_image_element.location_once_scrolled_into_view
                local_image_element.click()
                lib_TestSetUp.wait_for_page_to_load(wd_handle)
                print "MSG: Successfully clicked the Image element with locator:'%s'!!!" %ButtonLocator
                lib_TestSetUp.global_temp_element_locator = ''
                local_is_imageclicked = True
                return local_is_imageclicked
            except:
                local_image_element = Fnc_VerifyImageElementExist(wd_handle, ButtonLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        local_is_imageclicked = False
        assert False
    except:
        print "Error!!!Could not find the Image element with the locator: '%s'!!!" %ButtonLocator
        lib_TestSetUp.global_temp_element_locator = ''
        local_is_imageclicked = False
        assert False
    finally:
        return local_is_imageclicked

def is_image_enabled(wd_handle, ButtonLocator):
    try:
        local_image_element = Fnc_VerifyImageElementExist(wd_handle, ButtonLocator)
        while local_image_element is not None:
            try:
                local_bool_isenabled = local_image_element.is_enabled()
                lib_TestSetUp.global_temp_element_locator = ''
                return local_bool_isenabled
            except:
                local_image_element = Fnc_VerifyImageElementExist(wd_handle, ButtonLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        local_bool_isenabled = False
        assert False
    except:
        print "Error!!!Could not find the Button element with the locator: '%s'!!!" %ButtonLocator
        lib_TestSetUp.global_temp_element_locator = ''
        local_bool_isenabled = False
        assert False
    finally:
        return local_bool_isenabled

def Fnc_VerifyImageElementExist(wd_handle, ButtonLocator):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        local_image_element = lib_TestSetUp.is_element_present(wd_handle,ButtonLocator)
        return local_image_element
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

    
def Fnc_VerifyImageToolTip(Button, Expected_ToolTipValue):
    #Verify ToolTip by the element title
    try:
        local_actual_imagetooltip = Fnc_CheckImageToolTipExists(Button)
        assert_true(Button.get_source().contains(Expected_ToolTipValue))
        try:
            if local_actual_imagetooltip == Expected_ToolTipValue:
                print "MSG: Actual Tooltip value is '%s', and the  Expected Tooltip value is '%s'!" %(local_actual_imagetooltip,Expected_ToolTipValue)
                return True
            else:
                print "WARN: Actual Tooltip value is '%s', But Expected Tooltip value is '%s'!" %(local_actual_imagetooltip,Expected_ToolTipValue)
                return False
        except:
            print "MSG: Tooltip does not exist for '%s' button" % str(Button)
        return True
    except:
        return False
   
def Fnc_CheckImageToolTipExists(Button):
    try:
        local_actual_imagetooltip = Button.get_attribute('title')
        if local_actual_imagetooltip:
            return local_actual_imagetooltip
        else:
            return False
    except:
        return False