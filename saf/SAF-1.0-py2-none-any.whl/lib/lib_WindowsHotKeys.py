'''
*********************************************************************
    Library Name    : Lib Windows Hot keys
    Usage           : Contains methods to execute various functions on windows dialogs using windows keyboard hot keys 
    ToDo            : identify all other windows options
=====================================================================
    Created By          :Hari N V
    Created Date        :09/09/2013
    Last Modified By    :Hari N V
    Last Modified Date  :09/23/2013
*********************************************************************
'''


import AutoItLibrary
import time

def select_window(WindowTitle, WindowText=""):
    
    '''
    *********************************************************************
    Keyword Name    : Select Window <not decided to expose yet>
    Usage           : This function activates identifies and activates the windows dialog to the front. 
    ToDo            : May need to expose in future
    =====================================================================
    Created By          :Hari N V
    Created Date        :09/23/2013
    Last Modified By    :Hari N V
    Last Modified Date  :09/23/2013
    *********************************************************************
    '''
    
    SAF_AutoIt = AutoItLibrary.AutoItLibrary()
    try:
        SAF_AutoIt.WinWait(WindowTitle, WindowText, 5)
        if SAF_AutoIt.WinExists(WindowTitle):
            SAF_AutoIt.WinActivate(WindowTitle)
            status = SAF_AutoIt.WinWaitActive(WindowTitle, "", 5)
            if status is None :
                print WindowTitle + " window is active"
            else:
                print WindowTitle + " window is NOT activated"
                status = 1
        else:
            print "Window: " + WindowTitle + " is not identified"
    except Exception as ex:
        print "Exception occurred executing command : %s" %ex
        status = -1
    finally:
        return status

def windows_press_key(WindowTitle, WindowText, Command_Key, Count=1):
    
    '''
    *********************************************************************
    Keyword Name    : Windows Press Key
    Usage           : Keyword will activate the windows dialog, based on Title and text, and clicks the specific windows commands. 
                      Works for both single and multiple command format ("Esc" or "ALT + F4")
                      Covers ALT, SHIFT, CONTROL and "Windows" like (Windows + R -> opens Run command)
    ToDo            : Handle AutoIt @error. 
    =====================================================================
    Created By          :Hari N V
    Created Date        :09/23/2013
    Last Modified By    :Hari N V
    Last Modified Date  :09/23/2013
    *********************************************************************
    '''
    
    SAF_AutoIt = AutoItLibrary.AutoItLibrary()

    try:
        #Activate window and proceed based only if it is active
        status = select_window(WindowTitle, WindowText)
        if status == -1:
            print status
            return status
        
        if " + " in Command_Key:
            Key_Press_Status = windows_press_multi_key(Command_Key)
            if not Key_Press_Status:
                print "MSG:Not a valid multiple key combination, Try using individual keys!!!"
                return False
            return Key_Press_Status
        else:        
            if Count == 1:
                Command_Key_Format = "{" + Command_Key + "}"
            else:
                Command_Key_Format = "{" + Command_Key + " " + str(Count)+ "}"
            print Command_Key_Format
            SAF_AutoIt.Send(Command_Key_Format)
            print Command_Key + " pressed successfully"
            time.sleep(1)
            return True
    except Exception as ex:
        print "Exception occurred during key press: %s " % ex
        return False

def windows_press_multi_key(Command_Key):
    
    '''
    *********************************************************************
    Keyword Name    : <no keyword>
    Usage           : Function to click multiple keywords. 
                      DO NOT CALL separately, part of "windows_press_key" keyword
    ToDo            : Handle AutoIt @error. 
    =====================================================================
    Created By          :Hari N V
    Created Date        :09/23/2013
    Last Modified By    :Hari N V
    Last Modified Date  :09/23/2013
    *********************************************************************
    '''
    
    SAF_AutoIt = AutoItLibrary.AutoItLibrary()

    Keys_List = Command_Key.split(" + ") 
    try:
        for index in range(len(Keys_List)):
            if Keys_List[index].lower() == "alt":
                Keys_List[index] = "!"
            elif Keys_List[index].lower() == "shift":
                Keys_List[index] = "+"
            elif Keys_List[index].lower() == "control" or Keys_List[index].lower() == "ctrl":
                Keys_List[index] = "^"
            elif Keys_List[index].lower() == "windows":
                Keys_List[index] = "#"

        Command_Key_Format = ''.join(Keys_List)
        SAF_AutoIt.Send(Command_Key_Format)
        print Command_Key + " pressed successfully"
        time.sleep(1)
        return True
    except Exception as ex:
        print "Exception occurred during Multi key press: %s " % ex
        return False

def windows_typetext(WindowTitle, Input):
    
    '''
    *********************************************************************
    Keyword Name    : Windows Typetext
    Usage           : Keyword will type the data provided into specific field or dialog. 
                      Takes care of special characters and few unicode text
    ToDo            : NIL
    =====================================================================
    Created By          :Hari N V
    Created Date        :09/23/2013
    Last Modified By    :Hari N V
    Last Modified Date  :09/23/2013
    *********************************************************************
    '''
    
    
    SAF_AutoIt = AutoItLibrary.AutoItLibrary()
    try:
        #Activate window and proceed based only if it is active
        status = False
        Window_Status = select_window(WindowTitle)
        if Window_Status == 0:
            return status
        SAF_AutoIt.Send(Input, 1)
        print "Input : " + Input + " is sent."
        time.sleep(1)
        status = True
    except Exception as ex:
        print "Exception occurred during sending input data: %s" %ex
    finally:
        return status

