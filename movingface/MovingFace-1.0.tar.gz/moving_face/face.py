# -*- coding:utf-8 -*-

import os
from .key import Key

LF = "\n"

class Face():

    DEFAULT_FACE = "(´・ω・｀)"
    SPACE = '  '

    def __init__(self, face='', display_pos=False):
        if face is '':
            face = self.DEFAULT_FACE

        # [WIP] read face from file
        #face = open('./sample/resource/face1.txt', 'r').read()

        self.face = face
        self.display_pos = display_pos

        # initialize face position
        self.x = 0
        self.y = 0

    def __repr__(self):
        return self.face

    def update(self, order):
        #help(Key)
        if order is Key.UP:
            if self.y > 0:
                self.y -= 1
        elif order is Key.DOWN:
            self.y += 1
        elif order is Key.RIGHT:
            self.x += 1
        elif order is Key.LEFT:
            if self.x > 0:
                self.x -= 1

    def draw(self):
        os.system('clear')
        if self.display_pos: self._draw_position()
        self._draw_explain()
        self._draw_face()

    def _draw_position(self):
        print('x:' + str(self.x) + ' ' + 'y:' + str(self.y))

    def _draw_explain(self):
        print("press 'q' key to quit")

    def _draw_face(self):
        print(LF * self.y)
        print(LF.join(map(lambda l: self.SPACE * self.x + l, str(self).split(LF))))
