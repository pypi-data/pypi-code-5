# -*- coding: utf-8 -*-
"""这只是个测试啦
"""
def print_lot(the_list,level = 0):
    """这个函数取一个位置参数
"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lot(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)

