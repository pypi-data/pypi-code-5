from lib_Operations_UILink import click_link
from lib_Operations_UIButton import click_button
from lib_Operations_UITextBox import type_in_textbox
from lib_TestSetUp import wait_for_page_to_load,is_element_present
from selenium.webdriver.support.ui import WebDriverWait

def login_cloudplayer(wd_handle, CPLandingPage_URL, UserName, Password):
    '''
    *********************************************************************
    Keyword Name    :Login Cloudplayer
    
    Usage           :Function takes Cloudplayer landing page URL, User name and Password
    
    Return Value    : True on Successful login and False otherwise
    
    ToDo            :NIL
    
    =====================================================================
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        
        wd_handle.get(CPLandingPage_URL)
        CurrentBrowser_Url = CPLandingPage_URL
        CurrentBrowser_Url = wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
        print "\nCurrent Browser URL is: ", CurrentBrowser_Url
        click_link(wd_handle, 'SAF_SignIn_Link')
        #click_button(wd_handle, 'CP_LandingPage_GetStarted_Button')
        #FrameworkLibrary().Fnc_switch_window(wd_handle,'NewWindow')
        #CurrentBrowser_Url = wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
        #print "\nCurrent Browser URL is: ", CurrentBrowser_Url
        #type_in_textbox(wd_handle, 'CP_LoginPage_EmailAddress_TextBox', UserName)
        #FrameworkLibrary().Fnc_switch_window(wd_handle,'OldWindow')
        try:
            
            type_in_textbox(wd_handle, 'SAF_EmailAddress_TextBox', UserName)
        except:
            print "Error!!! Could not find the element to type Username"
            assert False
        try:
            type_in_textbox(wd_handle, 'SAF_Password_TextBox', Password)
        except:
            print "Error!!! Could not find the element to type Password"
            assert False
        try:
            click_button(wd_handle, 'SAF_SignIn_Button')
        except:
            print "Error!!! Could not find the element Signin button"
            assert False
        try:
            CurrentBrowser_Url = wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
            print "\nCurrent Browser URL is: ", CurrentBrowser_Url
            SignInButton = is_element_present(wd_handle, "SAF_SignIn_Button")
            if SignInButton is False:
                print "User ", UserName,' has been Logged in Successfully!!!'
                return True
            else:
                print "Error!!! ,User", UserName,' could not be logged in, Please check the username and password again !!!'
                return False
        except:
            print '\nError!!! Login Failed'
            assert False
            return False
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        print '\n!!!Exception occurred during Login, Could not load the login page and test Failed'
        return False

def select_songs(wd_handle,NumberOfSongsToSelect = -1):
    '''
    *********************************************************************
    Keyword Name    :Select Songs
    
    Usage           :Function takes driver handle and selects all songs in the songs view. If the optional number of songs to be selected is provided it will select only till the number specified.
    
    Return Value    : True if selected the number of songs and False otherwise
    
    ToDo            :NIL
    
    =====================================================================
    Created By          :Karthick Mani
    
    Created Date        :07/12/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :08/12/2013
    *********************************************************************
    '''
    try:
        #YourTable = is_element_present(wd_handle,'table')
        #TableRows = wd_handle.find_elements(By.TAG_NAME, 'tr')
        NumberOfSongs = int(wd_handle.find_element_by_id('songsLinkCount').text)
        if NumberOfSongsToSelect != -1:
            NumberOfSongs = int (NumberOfSongsToSelect)
        WebDriverWait(wd_handle, 10).until(lambda driver :wd_handle.find_element_by_css_selector("#tableContainer div.bodyContainer"))
        for i in range (0,NumberOfSongs):
            if i > 501:
                print "MSG: Successfully selected 500 Tracks in Cloud player!!!"
                break
            Xpath_CheckBox = "//tr[@idx='"+str(i)+"']/td/input[@class='checkbox']"
            Element_CheckBox = wd_handle.find_element_by_xpath(Xpath_CheckBox)
            if i % 50== 0:
                Element_CheckBox.location_once_scrolled_into_view
            if not Element_CheckBox.is_selected():
                Element_CheckBox.click()
        if NumberOfSongs < 500:
            print "MSG: Successfully selected %s Tracks in Cloud player!!!" % NumberOfSongs
        return True
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False