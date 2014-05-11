'''
Created on Nov 5, 2012

@author: karthicm
'''

from selenium.webdriver.support.ui import WebDriverWait

def is_element_present(WD_Browser,Locator_type,value):
    """
    This function waits for an element to appear on a given page for specified amount of time
    The function takes 3 agruments - webdriver_handle,method to search the element eg, xpath , id or css and element xpath or id or css selector to identify the element.
    """
    print "Action : checking if element present : "+value+"\n"
    try:
        if Locator_type == "xpath":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_element_by_xpath(value))
        elif Locator_type == "id":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_element_by_id(value))
        elif Locator_type == "css":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_element_by_css_selector(value))
        elif Locator_type == "name":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_elements_by_name(value))
        elif Locator_type == "link_partialtext":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_elements_by_partial_link_text(value))    
        elif Locator_type == "link_text":
            element = WebDriverWait(WD_Browser, 5).until(lambda driver :WD_Browser.find_elements_by_link_text(value))    
        if element is not False:
            result = True
        else:
            result = False
    except:
        print 'Could not retrieve element: '+value+'\n'
        result = False
    return result
        
def is_text_present(WD_Browser, string):
    """
    This function checks if a text is present in the HTML web source
    The function takes 2 agruments - webdriver_handle, and string
    """
    if str(string) in WD_Browser.page_source:
        return True
    else:
        return False
    
def click_flashPlayer_buttons(WD_Browser, resultFile):
    '''
    Checks functionality of flash player buttons on detail pages.
    '''
    '''
    Karthick initialized to "" this temporarily
    '''
    PLAY_ALL_BUTTON = ""
    TEST_FAILED = ""
    NEXT_BUTTON = ""
    PREVIOUS_BUTTON = ""
    
    previous_button = False
    next_button = False
    try:
        play_all = WD_Browser.find_element_by_xpath(PLAY_ALL_BUTTON)
    except:
        resultFile.write(TEST_FAILED + "Play all button not present\n")
        return None
    play_all.click()
    WD_Browser.implicitly_wait(2)
    try:
        next_button = WD_Browser.find_element_by_xpath(NEXT_BUTTON)
        next_button.click()
        WD_Browser.implicitly_wait(2)
        resultFile.write("Next Button present\n")
    except:
        resultFile.write("Next preview button NOT present\n")
    try:
        previous_button = WD_Browser.find_element_by_xpath(PREVIOUS_BUTTON)
        previous_button.click()
        resultFile.write("Previous button present\n")
    except:
        resultFile.write("Previous Button NOT present\n")
    
    return (play_all and next_button and previous_button)