'''
Created on Jan 23, 2013

@author: karthicm
'''
from lib_Operations_UILink import click_link
from lib_Operations_UIButton import click_button
from lib_Operations_UITextBox import type_in_textbox
import lib_TestSetUp
import subprocess
import os
from selenium.webdriver.common.action_chains import ActionChains
global global_old_wd_handle

def start_exe(exe_dir, exe_name):
    try:
        startup_path = os.path.join(exe_dir, exe_name)
        args = [startup_path]
        exeprocess = subprocess.Popen(args, stdout=subprocess.PIPE)
        return exeprocess
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def stop_exe(exeprocess):
    try:
        exeprocess.kill()
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
            
class FrameworkLibrary():
    
    def Fnc_GetElementLocators(self, ActualDict,ExcelInput_Element_Name):
        if ActualDict.has_key(ExcelInput_Element_Name):
            ElementLocators = ActualDict[ExcelInput_Element_Name]
            #print "\n", ElementLocators
            for EachLocator in ElementLocators.iterkeys():
                if ElementLocators.get(EachLocator) == 'NA':
                    continue
                print "\n",EachLocator
                print "-",ElementLocators.get(EachLocator)
        
        print "\n\n",ExcelInput_Element_Name,"\t", len(ActualDict)
    
    def start_exe(self, exe_dir, exe_name):
        try:
            startup_path = os.path.join(exe_dir, exe_name)
            args = [startup_path]
            exeprocess = subprocess.Popen(args, stdout=subprocess.PIPE)
            return exeprocess
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            return False
    
    def stop_exe(self,exeprocess):
        try:
            exeprocess.kill()
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            
    def Login_User(self,wd_handle, Login_URL, UserName, Password):
        try:       
            wd_handle.get(Login_URL)
            CurrentBrowser_Url = Login_URL
            CurrentBrowser_Url = lib_TestSetUp.wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
            print "\nCurrent Browser URL is: ", CurrentBrowser_Url
            click_button(wd_handle, 'CP_LandingPage_GetStarted_Button')
            self.Fnc_switch_window(wd_handle,'New')
            CurrentBrowser_Url = lib_TestSetUp.wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
            print "\nCurrent Browser URL is: ", CurrentBrowser_Url
            type_in_textbox(wd_handle, 'CP_LoginPage_EmailAddress_TextBox', UserName)
            self.Fnc_switch_window(wd_handle,'Old')
            click_link(wd_handle, 'CP_LandingPage_SignIn_Link')
            type_in_textbox(wd_handle, 'CP_LoginPage_EmailAddress_TextBox', UserName)
            type_in_textbox(wd_handle, 'CP_LoginPage_Password_TextBox', Password)
            click_button(wd_handle, 'CP_LoginPage_SignIn_Button')
            CurrentBrowser_Url = lib_TestSetUp.wait_for_page_to_load(wd_handle, CurrentBrowser_Url)
            SignInButton = lib_TestSetUp.is_element_present(wd_handle, "CP_LoginPage_SignIn_Button")
            if SignInButton is False:
                print "User ", UserName,' has been Logged in Successfully!!!'
            else:
                print "!!!Error,User", UserName,' could not be logged in !!!'
            print "\nCurrent Browser URL is: ", CurrentBrowser_Url
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            print '\n!!!Error, Login Failed'
    
    def Fnc_switch_window(self,wd_handle, Window = 'NEW'):
        try:
            try:
                global global_old_wd_handle
                global_old_wd_handle
                pass
            except:
                global_old_wd_handle = None
            if global_old_wd_handle is None:
                global_old_wd_handle = wd_handle.current_window_handle
            if Window.upper() is 'NEW':
                New_wd_handle = wd_handle.window_handles[-1]
                wd_handle.switch_to_window(New_wd_handle)
            else:
                wd_handle.switch_to_window(global_old_wd_handle)
            return True
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            return False

    def Fnc_drag_and_drop(self,wd_handle, SourceElement,TargetElement):
        try:
            Elmt_Source = lib_TestSetUp.is_element_present(wd_handle, SourceElement)
            Elmt_Target = lib_TestSetUp.is_element_present(wd_handle, TargetElement)
            ActionChains(wd_handle).drag_and_drop(Elmt_Source, Elmt_Target).perform()
        except Exception as ex:
            if ex:
                print 'Exception error is: %s' % ex
            print '\n!!!Error, Sorry could not drag and drop'+ SourceElement +' & '+ TargetElement
                        

    def Fnc_ValidateElementType(self,ExcelInput_Element_Name):
        Temp = ExcelInput_Element_Name.split('_')
        ElementType = str(Temp[len(Temp)-1])
        print ElementType, '+', len(Temp)
        
        if ElementType == 'Link':
            print 'Found Link, Call Link Module'
        elif ElementType == 'ImageLink':
            print 'Found ImageLink, Call ImageLink Module'
        elif ElementType == 'TextBox':
            print 'Found TextBox, Call TextBox Module'
        elif ElementType == 'Button':
            print 'Found Button, Call Button Module'
        elif ElementType == 'RadioButton':
            print 'Found RadioButton, Call RadioButton Module'
        elif ElementType == 'Text':
            print 'Found Text, Call Text Module'
        elif ElementType == 'Image':
            print 'Found Image, Call Image Module'
        elif ElementType == 'DropDownList':
            print 'Found DropDownList, Call DropDownList Module'
        elif ElementType == 'FlashButton':
            print 'Found FlashButton, Call FlashButton Module'
        else:
            print '!!! Warning : Element Type not Defined!!!'
        print ExcelInput_Element_Name
        