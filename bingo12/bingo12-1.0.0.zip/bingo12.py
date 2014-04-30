# -*- coding: utf-8 -*-
"""这只是个测试啦
"""
def print_lot(the_list):
    """这个函数取一个位置参数
"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lot(each_item)
        else:
            print(each_item)

