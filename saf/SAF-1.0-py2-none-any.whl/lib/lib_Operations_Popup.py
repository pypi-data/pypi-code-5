'''
Created on Jul 11, 2013

@author: karthicm
'''

def accept_popup(wd_handle):
    local_alert = wd_handle.switch_to_alert()
    local_alert.Alert.accept
    
def dismiss_popup(wd_handle):
    local_alert = wd_handle.switch_to_alert()
    local_alert.Alert.dismiss
    
def gettext_popup(wd_handle):
    local_alert = wd_handle.switch_to_alert()
    local_alert.Alert.text


def typein_popup(wd_handle,KeysToSend):
    local_alert = wd_handle.switch_to_alert()
    local_alert.Alert.send_keys(KeysToSend)
    
'''
Autoit.Send("{1}")
Autoit.Send("{+}")
Autoit.Send("{1}") 
Autoit.Send("{ENTER}")
'''
        
'''
from _winreg import *

"""print r"*** Reading from SOFTWARE\Microsoft\Windows\CurrentVersion\Run ***" """
aReg = ConnectRegistry(None,HKEY_CURRENT_USER)

hKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r"Environment")
value, type = _winreg.QueryValueEx (hKey, "PATH")
print value
'''



'''
SAF_Autoit = AutoItLibrary.AutoItLibrary()
Keywords = SAF_Autoit.get_keyword_names()
for key in Keywords:
    print key
'''