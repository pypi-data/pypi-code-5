# -*- coding:utf-8 -*-

import sys
import termios
import tty

class Key():

    UP, DOWN, RIGHT, LEFT, QUIT = 'up', 'down', 'right', 'left', 'quit'

    # Allow and Vim keys
    keys = {
        65: UP,
        66: DOWN,
        67: RIGHT,
        68: LEFT,
        107: UP, # k
        106: DOWN, # j
        108: RIGHT, # l
        104: LEFT, # h
        113: QUIT, # q
    }

    def __init__(self):
        self.input_stream = sys.stdin
        self.fd = self.input_stream.fileno()
        self.old = termios.tcgetattr(self.fd)

    def press(self):
        tty.setcbreak(self.fd)
        termios.tcflush(self.input_stream, termios.TCIOFLUSH)
        ch = self.input_stream.read(1)
        return self.keys.get(ord(ch)) if ch else None

    def terminate(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
