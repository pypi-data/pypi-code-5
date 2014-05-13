# -*- coding: utf-8 -*-

'''
Created on 2013 12 2

@author: dsedad
'''
# None use this,
class AppException(Exception):
    pass

class DbException(Exception):
    pass

class WrongActKey(AppException):
    def __str__(self):
        return 'Nekorektan aktivacijski kod'
        