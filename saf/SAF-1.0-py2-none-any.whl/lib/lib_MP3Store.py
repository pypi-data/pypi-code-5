'''
Created on Jun 13, 2013

@author: karthicm
'''
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

def return_asin_from_detailpage(wd_handle):
    '''
    *********************************************************************
    Keyword Name    :Return Asin From Detailpage
    Usage           :Function returns the ASIN from the MP3 detail page based on the Current URL. You can also try using return_substring_from_browserurl to return a particular value from the Browser URL
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :05/10/2013
    Last Modified By    :Karthick Mani
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    CurrentURL = str(wd_handle.current_url)
    print CurrentURL
    AsinInCurrentURL =  CurrentURL[CurrentURL.find('/dp/')+len('/dp/'):CurrentURL.find('/ref=')]
    return AsinInCurrentURL
    