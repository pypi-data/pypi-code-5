'''
Created on 2014/5/1

@author: MIMI
'''
dataset=[]
dataset=[  """ test"""
        
        "LIN NIGEL",36,"CHANG LINDA",31,
        ["CHILDS",
         ["TOTO",2.744,"BEBE",0.5
          ]]]
level=0
def getPrint(dataset,indent=False,level=0):
    for i in dataset: 
        if isinstance(i,list):
            getPrint(i,level+1)
        else:
            if indent:
                for tabstop in range(level):
                    print("\t",end='')
                print(i)
            
getPrint(dataset,level)