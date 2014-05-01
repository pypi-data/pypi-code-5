'''
Created on 2014/5/1

@author: MIMI
'''
dataset=[]
def getPrint(dataset):
    for i in dataset: 
        if isinstance(i,list):
            getPrint(i)
        else:
            print(i)
            
getPrint(dataset)