class CLS_MasterDictionaryBySheet:
    
    def __init__(self, Str_ExcelPath, Str_SheetName):
        self.Dict_Temp = {}
        self.Dict_MasterDictionary = {}
        self.Dict_MasterDictionaryTemp = {}
        self.Dict_MasterDictionary1 = {}
        
    def Fnc_GetKeyElementIndex(self,Str_ExcelPath, Str_SheetName):
        
        import xlrd
        Str_ExcelName = xlrd.open_workbook(str(Str_ExcelPath)) # Open excel work book
        Str_ActiveSheet = Str_ExcelName.sheet_by_name(Str_SheetName) # select the sheet req
        
        List_ColValues = Str_ActiveSheet.row_values(0)
        
        try:
            Int_ColIndex = List_ColValues.index('Element_Name') # identify which column in first row has Element_name
        
        except ValueError:
            print "'Element_Name' is not found in excel sheet's first row. Check excel file path, sheetname and first row and then check for the variable values"
            exit()
        
        return Int_ColIndex
    
    
    def Fnc_ElementCreateDictByRow(self,Str_SheetName, Int_ColIndex, Str_ExcelPath):
        
        import xlrd
        Str_ExcelName = xlrd.open_workbook(str(Str_ExcelPath)) # Open excel work book
        Str_ActiveSheet = Str_ExcelName.sheet_by_name(Str_SheetName)
        
        self.Dict_MasterDictionaryTemp = {}
        
        for Int_RowCount in range(1, Str_ActiveSheet.nrows):
            
            self.Dict_Temp = {}
            
            for Int_ColCount in range(Str_ActiveSheet.ncols):
                
                self.Dict_Temp[Str_ActiveSheet.cell(0,Int_ColCount).value] = Str_ActiveSheet.cell(Int_RowCount,Int_ColCount).value
            
            self.Dict_MasterDictionaryTemp[str(Str_ActiveSheet.cell(Int_RowCount,Int_ColIndex).value)] = self.Dict_Temp
            
        return self.Dict_MasterDictionaryTemp
    
    def Fnc_PageCreateDictByRow(self,Str_SheetName, List_ColValues, Str_ExcelPath, Str_PageTest):
        import xlrd
        Str_ExcelName = xlrd.open_workbook(str(Str_ExcelPath)) # Open excel work book
        Str_ActiveSheet = Str_ExcelName.sheet_by_name(Str_SheetName)
        self.Dict_MasterDictionaryTemp = {}
        try:
            Int_ColIndex = List_ColValues.index('Element_Name') # identify which column in first row has Element_name
            Int_PageColIndex = List_ColValues.index('PageTest') # identify which column in first row has PageTest
        except ValueError:
            print "'Element_Name' or 'PageTest' is not found in excel sheet's first row. Check excel file path, sheetname and first row and then check for the variable values"
            exit()
        for Int_RowCount in range(1, Str_ActiveSheet.nrows):            
            self.Dict_Temp = {}
            if str(Str_ActiveSheet.cell(Int_RowCount,Int_PageColIndex).value) == Str_PageTest:
                for Int_ColCount in range(Str_ActiveSheet.ncols):                    
                    self.Dict_Temp[Str_ActiveSheet.cell(0,Int_ColCount).value] = Str_ActiveSheet.cell(Int_RowCount,Int_ColCount).value
                self.Dict_MasterDictionaryTemp[str(Str_ActiveSheet.cell(Int_RowCount,Int_ColIndex).value)] = self.Dict_Temp
        return self.Dict_MasterDictionaryTemp
        
    def Fnc_ReturnElementMasterDict(self,Str_ExcelPath, Str_SheetName):
        List_ColValues = self.Fnc_GetKeyElementIndex(Str_ExcelPath, Str_SheetName)
        self.Dict_MasterDictionary = self.Fnc_ElementCreateDictByRow(Str_SheetName, List_ColValues, Str_ExcelPath)
        return self.Dict_MasterDictionary

    def Fnc_ReturnPageMasterDict(self,Str_ExcelPath,Str_SheetName, Str_PageTest):
        List_ColValues = self.Fnc_GetKeyElementIndex(Str_ExcelPath, Str_SheetName)
        self.Dict_MasterDictionary = self.Fnc_PageCreateDictByRow(Str_SheetName, List_ColValues, Str_ExcelPath, Str_PageTest)
        return self.Dict_MasterDictionary