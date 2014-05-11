'''
Created on Jan 24, 2013

@author: karthicm
'''
from lib_Operations_Common import get_webelement_attribute
import lib_TestSetUp
      
def type_in_textbox(wd_handle,TextBoxLocator,TextToType,IsConfidential = False):
    '''
    *********************************************************************
    Keyword Name    :Type In TextBox
    Usage           :Function finds the Textbox with given TextBoxLocator and types in the TextToType
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        local_element_textbox = Fnc_VerifyTextBoxElementExist(wd_handle, TextBoxLocator)
        while local_element_textbox is not None:
            try:
                local_element_textbox.location_once_scrolled_into_view
                local_element_textbox.clear()
                local_element_textbox.send_keys(TextToType)
                #TypedText = str(get_webelement_attribute(TextBox_Element,'value'))
                #if TypedText != TextToType:
                #    type_in_textbox(wd_handle, TextBoxLocator, TextToType)
                #else:
                if IsConfidential is not False:
                    print "MSG:Successfully typed the text in the Text Box %s" %(TextBoxLocator)
                else:
                    print "MSG:Successfully typed the text ('%s') in the Text Box %s" %(TextToType,TextBoxLocator)
                lib_TestSetUp.global_temp_element_locator = ''
                is_texttyped_in_textbox = True
                return is_texttyped_in_textbox
            except:
                local_element_textbox = Fnc_VerifyTextBoxElementExist(wd_handle, TextBoxLocator)
        lib_TestSetUp.global_temp_element_locator = ''
        is_texttyped_in_textbox = False
        assert False
    except:
        print "Error!!!Could not find the TextBox element with the locator: " + TextBoxLocator
        lib_TestSetUp.global_temp_element_locator = ''
        is_texttyped_in_textbox = False
        assert False
    finally:
        return is_texttyped_in_textbox
    
def gettext_in_textbox(wd_handle,TextBoxLocator):
    try:
        local_element_textbox = Fnc_VerifyTextBoxElementExist(wd_handle, TextBoxLocator)
        local_typedtext = str(get_webelement_attribute(local_element_textbox,'value'))
        lib_TestSetUp.global_temp_element_locator = ''
        return local_typedtext
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        lib_TestSetUp.global_temp_element_locator = ''
        return False    

def assert_typedtextcontent(wd_handle,TextBoxLocator,ExpectedText):
    try:
        local_typedtext = gettext_in_textbox(wd_handle, TextBoxLocator)
        if str(local_typedtext) == str(ExpectedText):
            print "Successfully Validated the text ('%s') is typed in the text box!!!" %local_typedtext
            lib_TestSetUp.global_temp_element_locator = ''
            return True
        else:
            print "Error the text typed ('%s') in the text box did not match with the expected text ('%s')" % (local_typedtext,ExpectedText)
            lib_TestSetUp.global_temp_element_locator = ''
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        lib_TestSetUp.global_temp_element_locator = ''
        return False   
    
def Fnc_VerifyTextBoxElementExist(wd_handle,TextBoxLocator):
    try:
        #Button = is_element_present(wd_handle,ButtonLocator,'XPATH', IsMultiple)
        local_element_textbox = lib_TestSetUp.is_element_present(wd_handle,TextBoxLocator)
        return local_element_textbox
    except:
        return False