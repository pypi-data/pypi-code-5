'''
Created on Dec 20, 2012

@author: karthicm
'''

class Dictonary:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        Dictonary.MasterDict = {} 
        Dictonary.CP_LandingPage_GetStarted_Link = {'PageTest': 'CP_LandingPage', 'Element_Name':'CP_LandingPage_GetStarted_Link','DisplayText_Value':'','Xpath_Relative(IdRelative)':'//div[@id=\'top\']/table/tbody/tr/td/map/area[2]','XpathLink':'','CSS':'area[alt="Get started"]','Id':'','Name':'','DomName':'','XpathAttributes':'','Link':''} 
        Dictonary.CP_LoginPage_ForgotPassword = {'PageTest': 'CP_LoginPage', 'Element_Name':'CP_LoginPage_ForgotPassword_Link','DisplayText_Value':'exact:Forgot your password?','Xpath_Relative(IdRelative)':'//span[@id=\'ap_small_forgot_password_span\']/a','XpathLink':'//a[contains(text(),\'Forgot your password?\')]','CSS':'#ap_small_forgot_password_span > a','Id':'','Name':'','DomName':'','XpathAttributes':'','Link':'exact:Forgot your password?'}
        Dictonary.Dict3 = {'PageTest': 'Value01', 'Element_Name':'Value02','DisplayText_Value':'Value03','Xpath_Relative(IdRelative)':'','XpathLink':'','CSS':'','Id':'','Name':'','DomName':'','XpathAttributes':'','Link':''}
        Dictonary.MainDict = {"CP_LandingPage_GetStarted_Link":Dictonary.CP_LandingPage_GetStarted_Link,"CP_LoginPage_ForgotPassword_Link":Dictonary.CP_LoginPage_ForgotPassword}
        
    def DisplayDictValues(self):
        print "Dictionary value of CP_LandingPage_GetStarted_Link", str(Dictonary.CP_LandingPage_GetStarted_Link)
        print "Dictionary value of CP_LoginPage_ForgotPassword_Link", str(Dictonary.CP_LoginPage_ForgotPassword)
        print "Dictionary value of Dict3", str(Dictonary.CP_LoginPage_ForgotPassword_Link)
        print "Dictionary value of MainDict", str(Dictonary.MainDict)
    
    def GetDictionary(self,Dict):
        self.Dict = Dict
        return Dict

    def GetElementDictionary(self,):
        if MasterDictionary.has_key('CP_LoginPage_ForgotPassword_Link'):
            ElementDictionary = Dict_Obj.GetDictionary()

    def CreateMasterDictionary(self,name,value):
        Dictonary.MasterDict[name] = value
        return Dictonary.MasterDict
        
Dict_Obj = Dictonary()
#Dict_Obj.DisplayDictValues()
#CP_LoginPage_ForgotPassword_Link
'''
TempDictName = Dict_Obj.GetDictionary(Dictonary.CP_LoginPage_ForgotPassword)
ElementDictionary = str(TempDictName.get('Element_Name'))
print str(ElementDictionary)
tempMaster = Dict_Obj.CreateMasterDictionary(ElementDictionary, TempDictName)
print str(tempMaster)
'''
MasterDictionary = Dict_Obj.GetDictionary(Dictonary.MainDict)
if MasterDictionary.has_key('CP_LoginPage_ForgotPassword_Link'):
    ElementDictionary = MasterDictionary.get('CP_LoginPage_ForgotPassword_Link')
    print ElementDictionary.get('DisplayText_Value')
    