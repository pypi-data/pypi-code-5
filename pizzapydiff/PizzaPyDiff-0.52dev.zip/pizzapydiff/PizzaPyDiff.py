#!/usr/bin/env python

"""This module allows for order agnostic comparison‎ of XML data. It will 
parse files to determine if they are a match while ignoring the order 
of attributes or duplicate nodes."""


import xml.etree.ElementTree as ET

def xml_to_list(oNode, oList, sXPath, iLevel=0):
    sXPath = sXPath + '/%s' % oNode.tag
    oList.append((sXPath, oNode.attrib, oNode.text, iLevel))
    for oChild in oNode:
        xml_to_list(oChild, oList, sXPath, iLevel=iLevel+1)

def xml_diff(data1, data2, bVerbose=False):
    if type(data1) is str and type(data2) is str:
        try:
            oRoot1 = ET.fromstring(data1)
        except Exception, e:
            print "Error parsing first string: %s" % e
            return False
        try:
            oRoot2 = ET.fromstring(data2)
        except Exception, e:
            print "Error parsing second string: %s" % e
            return False
        
    elif type(data1) is file and type(data2) is file: 
        try:
            oXml1 = ET.parse(data1)
            oRoot1 = oXml1.getroot()
        except Exception, e:
            print "Error parsing first file: %s" % e
            return False
        try:
            oXml2 = ET.parse(data2)
            oRoot2 = oXml2.getroot()
        except Exception, e:
            print "Error parsing second file: %s" % e
            return False

    else:
        print 'Unsupported file type, please see documentation. Supported types are file and string'
        return False
    
    sXPath = '' 
    oList1 = []
    oList2 = []
    
    xml_to_list(oRoot1, oList1, sXPath)
    xml_to_list(oRoot2, oList2, sXPath)
    
    bMatch = True
    
    for oValue in oList1:
        if oValue in oList2:
            oList2.remove(oValue)
            continue
        else:
            if(bVerbose):
                print 'Difference found in file one at: %s' % oValue[0] #where sXPath is stored
            bMatch = False
    if not oList2:
        return bMatch
    else:
        bMatch = False
        for oValue in oList2:
            if(bVerbose):
                print 'Difference found in file two at: %s' % oValue[0] #where sXPath is stored
        return bMatch

def _test():
    #Should return True
    sOrder1 = '<ItalianFood><Pizza Sauce="Red" Cheese="Mozzarella" Crust="Thin"><Quantity>2</Quantity></Pizza><Pizza Sauce="OliveOil" Cheese="Feta" Crust="Thin"><Quantity>1</Quantity></Pizza></ItalianFood>'
    sOrder2 = '<ItalianFood><Pizza Sauce="OliveOil" Cheese="Feta" Crust="Thin"><Quantity>1</Quantity></Pizza><Pizza Sauce="Red" Cheese="Mozzarella" Crust="Thin"><Quantity>2</Quantity></Pizza></ItalianFood>'
    print xml_diff(sOrder1, sOrder2)
    #Should return False
    sOrder1 = '<ItalianFood><Pizza Sauce="White" Cheese="Mozzarella" Crust="Thin"><Quantity>2</Quantity></Pizza><Pizza Sauce="OliveOil" Cheese="Feta" Crust="Thin"><Quantity>1</Quantity></Pizza></ItalianFood>'
    sOrder2 = '<ItalianFood><Pizza Sauce="OliveOil" Cheese="Feta" Crust="Thin"><Quantity>1</Quantity></Pizza><Pizza Sauce="Red" Cheese="Mozzarella" Crust="Thin"><Quantity>2</Quantity></Pizza></ItalianFood>'
    print xml_diff(sOrder1, sOrder2, True)
    
#     oFile1 = open(r'C:\Users\Administrator\Desktop\test1.xml', 'r')
#     oFile2 = open(r'C:\Users\Administrator\Desktop\test2.xml', 'r')
#     print xml_diff(oFile1, oFile2)

if __name__ == "__main__":
    _test()


