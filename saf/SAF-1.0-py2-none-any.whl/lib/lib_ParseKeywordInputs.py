'''
Created on Apr 19, 2013

@author: karthicm
'''
from lib_ReadInputData import Fnc_ReturnKeywordSequence
from lib_Operations_UILink import click_link
from selenium.selenium import selenium
from lib_Operations_UIButton import *
from lib_ReadInputData import Fnc_ReturnKeywordSequence
from CP_Web_SignInPage import login_cloudplayer
from lib_TestSetUp import open_browser
from lib_Operations_UITextBox import type_in_textbox
from lib_Operations_Common import  drag_and_drop 
from lib_Operations_UIDropDownList import select_from_dropdown
from lib_Operations_UICheckBox import SelectAutoRipCheckBox
from lib_Operations_Common import *
from lib_Operations_UIButton import click_button
from lib_Operations_UICheckBox import select_checkbox
from lib_FunctionLibrary import FrameworkLibrary
from lib_Browser import switch_window,navigate_browser
import exceptions
from lib_AmazonMusic import *

def ExecuteKeyword(wd_handle,Str_ExcelPath,Str_SheetName):
    try:
        Keyword_Queue = Fnc_ReturnKeywordSequence(Str_ExcelPath, Str_SheetName)
        Bln_Keyword = Bln_Arguments = Bln_MulitpleArguments = Bln_Value = Bln_Assertion = False
        while not Keyword_Queue.empty():
            FrameworkKeyword=Arguments=Value=None
            Keyword_Dict = Keyword_Queue.get()
            if Keyword_Dict.has_key('User_Keyword'):
                FrameworkKeyword = Keyword_Dict.get('User_Keyword')
                #print Keyword
                Bln_Keyword = True
            if Keyword_Dict.has_key('Keyword_Arguments'):
                Arguments = str(Keyword_Dict.get('Keyword_Arguments'))
                #print Arguments
                if "|" in Arguments:
                    Bln_MulitpleArguments = True
                Bln_Arguments = True
            if Keyword_Dict.has_key('Value'):
                Value = str(Keyword_Dict.get('Value'))
                #print Value
                Bln_Value = True
            if Keyword_Dict.has_key('AssertAndFail'):
                AssertAndFail = str(Keyword_Dict.get('AssertAndFail'))
                if AssertAndFail.upper() == 'TRUE':
                    Bln_Assertion = True
                else:
                    Bln_Assertion = False
            if not FrameworkKeyword == None:
                if Bln_MulitpleArguments == True:
                    ArgumentsList = CallBreakDownArguments(Arguments)
                    ExecuteKeywordWithMultipleArgs(wd_handle, FrameworkKeyword, ArgumentsList)
                    Bln_MulitpleArguments = False
                else:
                    KeywordParam = str(ExecuteKeywords(wd_handle, FrameworkKeyword, Arguments, Value))
                    ReturnedParms = KeywordParam.split('|')
                    print ReturnedParms[0]
                    print ReturnedParms[1]
                    if '-1' in str(ReturnedParms[1]):
                        if not Bln_Assertion == True:
                            print 'Warning: There was a problem executing the keyword:'+ str(ReturnedParms[0]) + '!!!'
                            assert True
                        else:
                            print 'Error: Could not execute the keyword:'+ str(ReturnedParms[0]) + ', Failing Testcase!!!'
                            assert False
                    else:
                        print 'Successfully executed the keyword: '+ str(ReturnedParms[0]) +' !!!'
                        pass
        print "All Keywords Executed"
        return True
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        print "Error Executing the Keywords"
        return False

def ExecuteKeywords(wd_handle,FrameworkKeyword,Arguments=None,Value=None):
    try:
        function = globals()[FrameworkKeyword]
        if Arguments == None and Value ==None:
            Keyword_return = function(wd_handle) 
            KeywordParam = str(FrameworkKeyword)+ '|' + str(Keyword_return)
        elif Value ==None:
            Keyword_return = function(wd_handle,Arguments)
            KeywordParam = str(FrameworkKeyword) + '(' + str(Arguments) + ')|' + str(Keyword_return)
        else:
            Keyword_return = function(wd_handle,Arguments,Value)
            KeywordParam = str(FrameworkKeyword) + '(' + str(Arguments) + ',' + str(Value) + ')|' + str(Keyword_return)
        return KeywordParam
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        return False

def ThrowWarning(wd_handle,KeywordParam):
    print 'Warning: There was a problem executing the keyword:'+ KeywordParam + '!!!'
    assert True
    
def ThrowError(wd_handle,KeywordParam):
    print 'Error: Could not execute the keyword:'+ KeywordParam + ', Failing Testcase!!!'
    assert False
    
def ExecuteKeywordWithMultipleArgs(wd_handle,FrameworkKeyword,ArgumentsList):
    try:
        function = globals()[FrameworkKeyword]
        Int_return = function(wd_handle,*ArgumentsList)
        print Int_return
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex
        raise
    
        
def CallBreakDownArguments(Arguments):
    ArgumentsList = Arguments.split("|")
    return ArgumentsList
