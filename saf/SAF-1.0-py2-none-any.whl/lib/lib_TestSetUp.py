# -*- coding: utf-8 -*- 
'''
Created on Oct 30, 2012

@author: karthicm
'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
from os.path import expanduser
import lib_CreateMasterDictionary
import framework_constants
import datetime
import lib_Operations_Common

global global_current_user
global global_target_browser
#global global_result_file
global global_str_excel_path
global global_str_excel_sheet_name
global global_bool_temp_dictionary
global global_temp_element_locator
global global_screenshot_directory
global global_dictionary_temp_elementlocators
global_temp_element_locator = ''

    
def Webdriver_Initiate(profile):
    """
    This function initializes the webdriver and creates handle to the correct browser. Browser informartion is seeked from a2ztestconfiguration file.
    This function takes a profile argument that sets up a custom profile for Firefox if necessary
    """
    try:
        if global_target_browser == 'FIREFOX' or global_target_browser == "FF":
            if profile:
                local_driver_handle = webdriver.Firefox(profile)
                local_driver_handle.implicitly_wait(5) # webdriver handle
            else:
                local_driver_handle = webdriver.Firefox()
                local_driver_handle.implicitly_wait(5)
        elif global_target_browser == 'CHROME':
            '''Simply calling the webdriver.Chrome() works for both mac and windows. The 
              other commented out lines are for reference for future troubleshooting use.'''
            #chromedriver = TEST_DIRECTORY+"/chromedriver"
            local_chrome_driver = framework_constants.CHROME_WEB_DRIVER
            try:
                os.environ["webdriver.chrome.driver"] = local_chrome_driver
                local_driver_handle = webdriver.Chrome(local_chrome_driver)
                local_driver_handle.implicitly_wait(5)
            #global_result_file.write("Current chromedriver in test directory is ONLY for WINDOWS. Download appropriate driver if on MAC! Comment out this line if not needed.")
            except:
                local_driver_handle = webdriver.Chrome() # webdriver handle
                local_driver_handle.implicitly_wait(5)
        if global_target_browser == 'IE' or global_target_browser == "INTERNET EXPLORER" or global_target_browser == "INTERNETEXPLORER":
            local_ie_driver = framework_constants.IE_WEB_DRIVER
            os.environ["webdriver.Ie.driver"] = local_ie_driver
            local_driver_handle = webdriver.Ie(local_ie_driver)
            local_driver_handle.implicitly_wait(5)
            #local_driver_handle = webdriver.Ie() # webdriver handle
        return local_driver_handle
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        local_driver_handle = False
        assert False
    finally:
        return local_driver_handle


def get_screenshot_directory():
    '''
    *********************************************************************
    Keyword Name    :Get Screenshot Directory
    Usage           :Return the user home screenshot directory 
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :10/01/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    '''
    return global_screenshot_directory

def open_browser(wd_handle,URL):
    '''
    *********************************************************************
    Keyword Name    :Open Browser
    Usage           :Open the given browser with the provided URL 
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        wd_handle.get(URL)
        wait_for_page_to_load(wd_handle)
        return True
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def is_element_present(wd_handle,ElementLocators_Constant,local_testelement_locator_type= None, BooleanAllElements = False,IsVisible = True):
    """
    This function waits for an element to appear on a given page for specified amount of time
    The function takes 3 agruments - webdriver_handle,method to search the element eg, xpath , id or css and element xpath or id or css selector to identify the element.
    """
    '''
    *********************************************************************
    Keyword Name     :is_element_present
    Usage           :This function waits for an element to appear on a given page for specified amount of time, The function takes Madatory 2 agruments webdriver_handle & Locator.
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    #print "Action : Checking if element present : "+ElementLocators_Constant
    try:
        global global_bool_temp_dictionary
        global global_temp_element_locator
        local_foundelement =local_result= local_set_locator_type=  False
        if global_temp_element_locator !=ElementLocators_Constant:
            global_temp_element_locator = ElementLocators_Constant
            global_bool_temp_dictionary = False
        if global_dictionary_element_mapping.has_key(ElementLocators_Constant):
            if global_bool_temp_dictionary is False:
                local_element_locators = global_dictionary_element_mapping[ElementLocators_Constant]
                global global_dictionary_temp_elementlocators
                global_dictionary_temp_elementlocators = local_element_locators.copy()
                global_bool_temp_dictionary = True
            else:
                local_element_locators = global_dictionary_temp_elementlocators.copy()
            #print "len(TempDict_ElementLocators): %s" % len(TempDict_ElementLocators)
            if not len(local_element_locators)>5:
                return None
            for local_each_locator in local_element_locators.iterkeys():
                if not local_each_locator in framework_constants.SAF_LOCATORS:
                    continue
                if local_element_locators.get(local_each_locator) == 'NA' or local_element_locators.get(local_each_locator)=='':
                    del global_dictionary_temp_elementlocators[local_each_locator]
                    continue
                #local_element_locators.get(local_each_locator)
                del global_dictionary_temp_elementlocators[local_each_locator]
                if local_testelement_locator_type is None:
                    local_testelement_locator_type = str(local_each_locator).upper()
                    local_set_locator_type = True
                elif local_set_locator_type == True:
                    local_testelement_locator_type = str(local_each_locator).upper()
                else:
                    local_testelement_locator_type = local_testelement_locator_type.upper()
                local_element_locators_value = str(local_element_locators.get(local_testelement_locator_type))
                if BooleanAllElements == False:
                    local_element_under_test = CheckElementPresent(wd_handle, local_element_locators_value,local_testelement_locator_type)
                else:
                    local_element_under_test = CheckElementsPresent(wd_handle, local_element_locators_value,local_testelement_locator_type)
                try:
                    if local_element_under_test is not False:
                        local_foundelement = True
                        break
                    else:
                        continue
                except:
                    continue
                             
        else:
            local_element_locators_value = ElementLocators_Constant
            if BooleanAllElements == False:
                local_element_under_test = CheckElementPresent(wd_handle, local_element_locators_value,local_testelement_locator_type)
                if local_element_under_test is not False:
                    local_foundelement = True
                else:
                    if local_element_under_test is not False and local_foundelement == False and local_element_under_test.is_displayed():
                        local_foundelement = True
            else:
                local_element_under_test = CheckElementsPresent(wd_handle, local_element_locators_value,local_testelement_locator_type)
                if not IsVisible == True:
                    if local_element_under_test is not False and local_foundelement == False:
                        local_foundelement = True
                else:
                    if local_element_under_test is not False and local_foundelement == False and local_element_under_test.is_displayed():
                        local_foundelement = True
        if local_foundelement:
            local_result = local_element_under_test
        else:
            local_result = None
    except Exception as ex:
            if ex:
                print 'Exception occurred: %s' % ex
            if not local_result:
                local_result = None
    finally:
        return local_result

def CheckElementPresent (wd_handle,ElementLocators_Value,local_testelement_locator_type = None):
    try:
        if local_testelement_locator_type is None:
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_id(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass 
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_name(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_css_selector(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_class_name(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass  
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_link_text(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_partial_link_text(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            try:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_tag_name(ElementLocators_Value))
                if local_element_under_test is not False:
                    return local_element_under_test
            except:
                local_element_under_test = False
                pass
            finally:
                return local_element_under_test
        else:
            if local_testelement_locator_type == "ID":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_id(ElementLocators_Value))
            elif local_testelement_locator_type == "NAME":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_name(ElementLocators_Value))
            elif local_testelement_locator_type == "CSS":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_css_selector(ElementLocators_Value))
            elif local_testelement_locator_type == "CLASS_NAME":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_class_name(ElementLocators_Value))
            elif "XPATH" in local_testelement_locator_type:
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_xpath(ElementLocators_Value))
            elif local_testelement_locator_type == "PARTIAL_LINKTEXT":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_partial_link_text(ElementLocators_Value))    
            elif local_testelement_locator_type == "LINKTEXT":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_link_text(ElementLocators_Value))
            elif local_testelement_locator_type == "TAG_NAME":
                local_element_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_element_by_tag_name(ElementLocators_Value))
            try:
                return local_element_under_test
            except:
                return False
    except Exception as ex:
        try:
            if ex and len(ex)>0:
                print 'Exception error is: %s' % ex
        except:
            pass
        return False

def wait_for_page_to_load(wd_handle,BrowserUrl = None):
    '''
    *********************************************************************
    Keyword Name    :Wait For Page To Load
    Usage           :This function will wait for the page to load on the given browser by waiting for the readystate value. 
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        local_browser_readystate_command = framework_constants.BROWSER_READYSTATE_COMMAND
        local_browser_readystate_value = wd_handle.execute_script(local_browser_readystate_command)
        while not local_browser_readystate_value == 'complete':
            local_browser_readystate_value = wd_handle.execute_script(local_browser_readystate_command)
            print "Loading page.... "#,local_browser_readystate_value
        local_ajaxload_verification = lib_Operations_Common.wait_for_ajax_to_load(wd_handle)     
        local_bowser_currenturl = str(wd_handle.current_url)
        if not BrowserUrl is None and BrowserUrl == local_bowser_currenturl:
            return local_ajaxload_verification
        elif BrowserUrl == local_bowser_currenturl:
            return BrowserUrl
        else:
            return wd_handle.current_url
    except Exception as ex:
        try:
            if ex and len(ex.msg)>0:
                print 'Exception error is: %s' % ex
        except:
            pass

def CheckElementsPresent (wd_handle,ElementLocators_Value,local_testelement_locator_type=None):
    try:
        if local_testelement_locator_type is None:
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_id(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_name(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_css_selector(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_class_name(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_xpath(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_partial_link_text(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_link_text(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            try:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_tag_name(ElementLocators_Value))
                if local_elements_under_test is not False:
                    return local_elements_under_test
            except:
                local_elements_under_test = False
                pass
            finally:
                return local_elements_under_test
        else:
            if local_testelement_locator_type == "ID":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_id(ElementLocators_Value))
            elif local_testelement_locator_type == "NAME":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_name(ElementLocators_Value))
            elif local_testelement_locator_type == "CSS":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_css_selector(ElementLocators_Value))
            elif local_testelement_locator_type == "CLASS_NAME":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_class_name(ElementLocators_Value))
            elif "XPATH" in local_testelement_locator_type:
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_xpath(ElementLocators_Value))
            elif local_testelement_locator_type == "PARTIAL_LINKTEXT":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_partial_link_text(ElementLocators_Value))
            elif local_testelement_locator_type == "LINKTEXT":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_link_text(ElementLocators_Value))
            elif local_testelement_locator_type == "TAG_NAME":
                local_elements_under_test = WebDriverWait(wd_handle, 5).until(lambda driver :wd_handle.find_elements_by_tag_name(ElementLocators_Value))
            return local_elements_under_test
    except Exception as ex:
        try:
            if ex and len(ex.msg)>0:
                print 'Exception error is: %s' % ex
        except:
            pass
        return False

def is_text_present(wd_handle, string):
    '''
    *********************************************************************
    Keyword Name    :Is Text Present
    Usage           :This function checks if a text is present in the HTML web source.\n The function takes 2 agruments - webdriver_handle, and string
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        if str(string) in wd_handle.page_source:
            return True
        else:
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex

'''            
def clean_up_before_test():
    """
    This function remove any test results from previous build in the test directory
    The function takes no argument. Creates a lgobal variable for all functions to 
    edit the opened file.
    """
    try:
        global global_result_file
        global_result_file.close()
        print os.path.isfile(RESULT_LOG_PATH)
        if os.path.isfile(RESULT_LOG_PATH) == True: 
            os.remove(RESULT_LOG_PATH)
        global_result_file = open(RESULT_FILE, 'a')
        
    except Exception as ex:
        if not ex:
            print 'Exception error is: %s' % ex
'''
            
def initiate_setup(BROWSER="Firefox",MappingExcelPath="ElementMappingExcelPath",ExcelSheetName="ElementMappingExcelSheetName",profile="default"):
    """
    This function is initial setup for each test script
    The function takes 2 agrument - self and a profile for Firefox, only if necessary
    """
    '''
    *********************************************************************
    Keyword Name    :Initiate Setup
    Usage           : Keyword will initiate the browser for the desired profile and Element mapping sheet for SAF. JavaScript_ON\JavaScript_OFF to enable and disable JS on browser.  
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        local_current_profile = False
        global global_target_browser
        global global_current_user
        global_current_user = expanduser("~")
        global_target_browser = (str(BROWSER)).upper()
        if (global_target_browser == "FIREFOX" or global_target_browser == "FF") and profile:
            print 'Selected Browser is FIREFOX!!!'
            local_current_profile = Setup_Firefox_Profile(profile) 
        wd_handle = Webdriver_Initiate(local_current_profile)
        print "Initiated browser Successfully %s" %wd_handle
        if global_target_browser == "CHROME" and profile:
            print 'Selected Browser is CHROME!!!'
            #Setup_Chrome_Plugin(wd_handle, profile)
        if (global_target_browser == "IE" or global_target_browser == "Internet Explorer") and profile:
            print 'Selected Browser is Internet Explorer!!!'
            # Developer for this part of the code did not have access to IE, also IE sucks.
        wd_handle.maximize_window()
        #base_url = HOMEPAGE_AMAZON
        #verificationErrors = []
        try:
            local_today = datetime.date.today()
            local_string_today = str(local_today)
            local_formatted_string_today = local_string_today.replace('-', '')
            local_formatted_string_today = local_formatted_string_today
            local_run_folder_status= lib_Operations_Common.get_current_result_directory()
            local_screenshot_directory = local_run_folder_status + "/screenshots"
            global_screenshot_directory = local_screenshot_directory
        except Exception as ex:
            print 'Exception occurred while creating run folder: %s' % ex
            pass
        '''
        if not os.path.exists(framework_constants.TEST_DIRECTORY+"/"+local_formatted_string_today):
            os.makedirs(framework_constants.TEST_DIRECTORY+"/"+local_formatted_string_today)
        UserHome = expanduser("~")
        if not os.path.exists(UserHome+"/"+framework_constants.SCREENSHOT_DIRECTORY_NAME):
            os.makedirs(UserHome+"/"+framework_constants.SCREENSHOT_DIRECTORY_NAME)
            global global_screenshot_directory
            global_screenshot_directory = UserHome+"/"+framework_constants.SCREENSHOT_DIRECTORY_NAME
        '''
        #resultFile = open(RESULT_FILE, 'a')  # opening file for output
        #global_result_file = resultFile
        
        try:
            global global_dictionary_element_mapping
            if MappingExcelPath !="ElementMappingExcelPath" and ExcelSheetName !="ElementMappingExcelSheetName":
                global global_str_excel_path
                global_str_excel_path = MappingExcelPath
                global global_str_excel_sheet_name
                global_str_excel_sheet_name = ExcelSheetName
                local_object_masterdictionary = lib_CreateMasterDictionary.CLS_MasterDictionaryBySheet(global_str_excel_path, global_str_excel_sheet_name)
                global_dictionary_element_mapping = local_object_masterdictionary.Fnc_ReturnElementMasterDict(global_str_excel_path, global_str_excel_sheet_name)
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            print "Warning!!!, ElementMapping Excel path and sheet name not defined correctly!!! \n Please provide correct path and sheet name (Or) Use the hard coded Locators in your tests"
            pass
        local_driver_handle =  wd_handle
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        local_driver_handle = False
        assert False
    finally:
        return local_driver_handle
    

'''
def Setup_Chrome_Plugin(wd_handle, plugin):
    """
    This function enables or disables the AMD plugin for Chrome, depending on the "plugin" preference
    Reasons this function may not work properly is due to the xpath to the "enable/disable" button for the plugin, it is relative
      to other plugins and this may be different for each individual and what plugins are installed. Or AMD was never installed!
    Arugments: Takes in the current webdriver handle (wd_handle) and the desired preference for plugin setup (plugin)
    """
    try:
        wd_handle.get(AMD_PLUGIN_CHROME) # Go to Chrome plugin settings page
        if plugin == "amd_on":
            try:
                wd_handle.implicitly_wait(3)
                wd_handle.find_element_by_xpath(AMD_ON).click() # Enable AMD plugin
            except:
                pass
                #global_result_file.write("AMD plugin is already enabled OR xpath may need to be revised (see Setup_Chrome_Plugin function documentation) OR AMD was never installed\n")
        elif plugin == "amd_off":
            try:
                wd_handle.implicitly_wait(3)
                wd_handle.find_element_by_xpath(AMD_OFF).click() # Disable AMD plugin
            except:
                pass
                #global_result_file.write("AMD plugin is already disabled OR xpath may need to be revised (see Setup_Chrome_Plugin function documentation) OR AMD was never installed\n")
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
'''
         
def Setup_Firefox_Profile(profile):
    """
    This function Enable/Disable the Amazon Download Manager plugin.
    Resource: http://kb.mozillazine.org/Creating_a_new_Firefox_profile_on_Windows
    The function takes 2 agruments - webdriver_handle, and if plugin needs to be set or not with value "True" or "False" respectively
    """
    try:
        local_new_ff_profile = False
        if profile == "m3u":
            local_new_ff_profile = webdriver.FirefoxProfile() #Set up custom webdriver profile for Firefox
            local_new_ff_profile.set_preference("browser.download.folderList",2)
            local_new_ff_profile.set_preference("browser.download.manager.showWhenStarting",False)
            local_new_ff_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/x-mpegurl") #Allow auto-downloading of m3u file
        elif profile == "JavaScript_ON":
            local_new_ff_profile = webdriver.FirefoxProfile()
            local_new_ff_profile.set_preference("browser.download.folderList",2)
            local_new_ff_profile.set_preference("javascript.enabled", True)
        elif profile == "JavaScript_OFF":
            local_new_ff_profile = webdriver.FirefoxProfile()
            local_new_ff_profile.set_preference("browser.download.folderList",2)
            local_new_ff_profile.set_preference("javascript.enabled", False)
        return local_new_ff_profile
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
            
def initiate_teardown(wd_handle,TEST_DIRECTORY=''):
    """
    This function is final teardown for each test script
    The function takes 1 agrument - self
    """
    '''
    *********************************************************************
    Keyword Name    :initiate_teardown
    Usage           :initiate_teardown is used to close all the browser instances and process the output files to the proper Run folders.
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :07/23/2013
    *********************************************************************
    '''
    try:
        wd_handle.quit()
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
