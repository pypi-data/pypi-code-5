'''
Created on Apr 15, 2013

@author: karthicm
'''
import Queue
from types import DictionaryType

Str_ExcelPath = "C:\Users\karthicm\Desktop\Selenium\InputData\TestCase_Template.xlsx"
Str_SheetName = "LoginUser"
Dict_Temp = {}

def Fnc_ReturnKeywordSequence(Str_ExcelPath, Str_SheetName):
    Int_ColIndex = Fnc_GetKeyElementIndex(Str_ExcelPath, Str_SheetName)
    Keyword_Queue = Fnc_CreateKeyWordQueue(Str_SheetName, Int_ColIndex, Str_ExcelPath)
    '''
    while not Keyword_Queue.empty():
        Keyword_Dict = Keyword_Queue.get()
        if Keyword_Dict.has_key('User_Keyword') or Keyword_Dict.has_key('Keyword_Arguments'):
            print str(Keyword_Dict.get('User_Keyword')) +','+ str(Keyword_Dict.get('Keyword_Arguments')) +','+ str(Keyword_Dict.get('Value'))
    '''
    return Keyword_Queue
    #print dict
    
def Fnc_GetKeyElementIndex(Str_ExcelPath, Str_SheetName):
    
    import xlrd
    #Str_ExcelPath = Str_ExcelPath
    #Str_SheetName = Str_SheetName
    Str_ExcelName = xlrd.open_workbook(str(Str_ExcelPath)) # Open excel work book
    Str_ActiveSheet = Str_ExcelName.sheet_by_name(Str_SheetName) # select the sheet req
    
    List_ColValues = Str_ActiveSheet.row_values(0)

    try:
        Int_ColIndex = List_ColValues.index('User_Keyword') # identify which column in first row has Element_name
    
    except ValueError:
        print "'User_Keyword' is not found in excel sheet's first row. Check excel file path, sheetname and first row and then check for the variable values"
        exit()
    
    return Int_ColIndex
    
def Fnc_CreateKeyWordQueue(Str_SheetName, Int_ColIndex, Str_ExcelPath):
    
    import xlrd
    ExcelName = xlrd.open_workbook(str(Str_ExcelPath)) # Open excel work book
    '''
    SheetNames = ExcelName.sheet_names()
    for sName in SheetNames:
        print sName
    '''
    Str_ActiveSheet = ExcelName.sheet_by_name(Str_SheetName)
    Keyword_Queue = Queue.Queue()
    for Int_RowCount in range(1, Str_ActiveSheet.nrows):
        
        Dict_Temp = {}
        
        for Int_ColCount in range(Str_ActiveSheet.ncols):
            if not Str_ActiveSheet.cell(Int_RowCount,Int_ColCount).value == '':
                Dict_Temp[Str_ActiveSheet.cell(0,Int_ColCount).value] = Str_ActiveSheet.cell(Int_RowCount,Int_ColCount).value
        Keyword_Queue.put(Dict_Temp)        
    return Keyword_Queue

#Fnc_ReturnKeywordSequence(Str_ExcelPath, Str_SheetName)

