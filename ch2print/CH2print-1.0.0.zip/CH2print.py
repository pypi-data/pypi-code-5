'''
Created on 2014/5/3

@author: nigel
'''
def print_get(datalist):
    for each_i in datalist:
        if isinstance(each_i,list):
            print_get(each_i)
        else:
            print(each_i)