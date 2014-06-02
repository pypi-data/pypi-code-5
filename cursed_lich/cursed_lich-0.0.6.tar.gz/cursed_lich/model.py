#!/usr/bin/env python

class Hero(object):
    
    def __init__(self):
        self.hp = (0, 0)
        self.mp = (0, 0)
        self._defense = 0

    @property
    def defense(self):
        return self._defense
    
    @defense.setter
    def defense(self, value):
        self._defense = value

