'''
Created on Nov 17, 2013

@author: karthicm
'''
OUTPUT_FILE_TYPES = ["log.html", "output.xml", "report.html"]
TEST_DIRECTORY = 'C:\SAF\OutputData\Reports'
SCREENSHOT_DIRECTORY_NAME = 'RF_Screenshot'
SAF_LOCATORS = ["ID","NAME","CSS","CLASS_NAME","PARTIAL_LINKTEXT","LINKTEXT","TAG_NAME","XPATHATTRIBUTES","XPATH_RELATIVE","XPATHLINK"]
CHROME_WEB_DRIVER = "C:\SAF\Drivers\chromedriver.exe"
IE_WEB_DRIVER = "C:\SAF\Drivers\IEDriverServer.exe"
BROWSER_READYSTATE_COMMAND = "return document.readyState"
BROWSER_JQUERY_EXECUTION_COMMAND = "return jQuery.active"
BROWSER_JQUERY_EXECUTION_UNDEFINED_COMMAND = "return window.jQuery != undefined && jQuery.active === 0"