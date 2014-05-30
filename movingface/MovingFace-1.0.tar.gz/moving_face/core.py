# -*- coding:utf-8 -*-

import sys
from .face import Face
from .key import Key

def start():
    try:
        face = Face(sys.argv[1])
    except IndexError:
        face = Face()

    key = Key()
    face.draw()

    try:
        while True:
            order = key.press()
            if order is not None:
                if order is Key.QUIT:
                    break
                face.update(order)
                face.draw()
    finally:
        key.terminate()
        sys.exit(0)
