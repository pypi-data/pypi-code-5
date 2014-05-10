# /usr/bin/python
from __future__ import print_function
import sys
import re

from enum import Enum


__author__ = "Alexander Weigl <alex953@gmail.com>"
__version__ = "0.2.1"
__date__ = "25. Jul. 2006"

#region constants
class Color16Table(Enum):
    DEFAULT = 39
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    Light_Gray = 37
    Dark_Gray = 90
    Light_Red = 91
    Light_Green = 92
    Light_Yellow = 93
    Light_Blue = 94
    Light_Cyan = 96
    White = 97
    Light_Magenta = 95


class Option(Enum):
    BOLD_ON = 1
    DIM_ON = 2
    UNDERLINE_ON = 4
    BLINK_ON = 5
    REVERSE_ON = 7
    HIDDEN_ON = 8
    RESET = 0
    BOLD_OFF = 21
    DIM_OFF = 22
    UNDERLINE_OFF = 24
    BLINK_OFF = 25
    REVERSE_OFF = 27
    HIDDEN_OFF = 28


CSI = "\033["

#endregion

def default_tags():
    d = {
        'y': style(Color16Table.Yellow),
        'r': style(Color16Table.Red),
        'g': style(Color16Table.Green),
        'b': style(Color16Table.Blue),
        'm': style(Color16Table.Magenta),
        'c': style(Color16Table.Cyan),

        'Y': style(background=Color16Table.Yellow),
        'R': style(background=Color16Table.Red),
        'G': style(background=Color16Table.Green),
        'B': style(background=Color16Table.Blue),
        'M': style(background=Color16Table.Magenta),
        'C': style(background=Color16Table.Cyan),

        'ly': style(Color16Table.Light_Yellow),
        'lr': style(Color16Table.Light_Red),
        'lg': style(Color16Table.Light_Green),
        'lb': style(Color16Table.Light_Blue),
        'lm': style(Color16Table.Light_Magenta),
        'lc': style(Color16Table.Light_Cyan),

        'LY': style(background=Color16Table.Light_Yellow),
        'LR': style(background=Color16Table.Light_Red),
        'LG': style(background=Color16Table.Light_Green),
        'LB': style(background=Color16Table.Light_Blue),
        'LM': style(background=Color16Table.Light_Magenta),
        'LC': style(background=Color16Table.Light_Cyan),

        'blink': style(option=Option.BLINK_ON),
        'ul': style(option=Option.UNDERLINE_ON)
    }

    for i in range(256):
        d["fg%d" % i] = style(foreground=i)
        d["bg%d" % i] = style(background=i)

    return d


class style(object):
    def __init__(self, foreground=None, background=None, option=set()):
        self.foreground = foreground
        self.background = background

        if hasattr(option, "__iter__"):
            self.option = option
        else:
            self.option = [option]

    def __copy(self):
        return style(self.foreground, self.background, self.option)

    def __str__(self):
        return "<style %s>" % str(iter(self))

    def __iter__(self):
        return (self.foreground, self.background, self.option)

    def extends(self, other):
        return self + other

    def __add__(self, other):
        new = self.__copy()

        if other.foreground:
            new.foreground = other.foreground

        if other.background:
            new.background = other.background

        if other.style:
            new.option = other.style

        return new


    @property
    def fgcode(self):
        if self.foreground:
            if isinstance(self.foreground, Color16Table):
                return "%dm" % self.foreground.value
            else:
                return "38;5;%dm" % self.foreground
        return None

    @property
    def bgcode(self):
        if self.background:
            if isinstance(self.background, Color16Table):
                return "%dm" % self.background.value + 10
            else:
                return "48;5;%dm" % self.background
        return None

    @property
    def opcode(self):
        if self.option:
            return ";".join(map(lambda x: str(x), self.option)) + "m"


from StringIO import StringIO


class term:
    """
    A AnsiTerminal is a wrapper above a handle for writing ansi sequences to terminals.
    With the attribute @enabled@ you can block all ansi sequences for printout
    """

    def __init__(self, handle=sys.stdout, enabled=True):
        """
        Create a new AnsiTerminal for the file/console handle.
        The default is enable true and the handle is sys.stdout
        """
        self.output = handle
        self.buffer = StringIO()
        self.enabled = enabled  # and handle.isatty():

        self._register = default_tags()
        self.startenv = r"{"
        self.endenv = r"}"

        self.normal_style = style(option=Option.RESET)

    def __lshift__(self, obj):
        self.output.write(obj)

    def set_raw(self, *args):
        """
        writes all *args as styled commands 'm' to the handle
        """
        if not self.enabled: return
        args = map(lambda x: str(x), [x for x in args if x is not None])
        self._write_raw(';'.join(args) + 'm')

    def _write_raw(self, suffix):
        """
        writes a the suffix prefixed by the CSI to the handle
        """
        if not self.enabled: return

        self.buffer.write(CSI)
        self.buffer.write(suffix)

    def register(self, tag, style):
        self._register[tag] = style

    def get_normal(self):
        return self.normal_style

    def activate_style(self, style):
        if style.foreground:
            self._write_raw(style.fgcode)

        if style.background:
            self._write_raw(style.bgcode)

        if style.option:
            self._write_raw(style.opcode)

    def get_style(self, tag):
        try:
            return self._register[tag]
        except KeyError as e:
            return self.get_normal()

    def cprint(self, string):
        stack = []
        self.buffer = StringIO()

        def nextword():
            s = ""
            for c in char_iter:
                if c == " ": break;
                s += c
            return s

        def pop():
            try:
                stack.pop()
                self.activate_style(self.get_normal())
                peak()
            except:
                pass

        def push():
            tag = nextword()
            stack.append(tag)
            peak()

        def peak():
            try:
                t = stack[-1]
                self.activate_style(self.get_style(t))
            except KeyError as e:
                pass

        char_iter = iter(string)
        for c in char_iter:
            if c == self.startenv:
                push()
            elif c == self.endenv:
                pop()
            else:
                self.buffer.write(c)

        self.output.write(self.buffer.getvalue())


    #def printr(self, *objects, sep=' ', end='\n'):
    def printr(self, *objects):
        sep = ' '
        end = "\n"

        for o in objects:
            self.cprint(str(o))
            self.output.write(sep)
        self.output.write(end)


    def flag(self, option):
        self.set_raw(option.value)

    def scroll_page_up(self, page=1):
        """
        Command: CSI n S
        Name:    SU
        Scroll whole page up by n (default 1) lines. New lines are added at the bottom. (not ANSI.SYS)
        """
        self._write_raw(page + 'S')

    def scroll_page_down(self, page=1):
        """
        Command: CSI n T
        Name:    SD
        Scroll whole page down by n (default 1) lines. New lines are added at the top. (not ANSI.SYS)
        """
        self._write_raw(page + 'T')

    def clear_screen(self, type=2):
        """
        Command: CSI n J
        Name; ED
        Clears part of the screen. If n is zero (or missing), clear from cursor to end of screen. If n is one, clear from cursor to beginning of the screen. If n is two, clear entire screen (and moves cursor to upper left on MS-DOS ANSI.SYS).
        """
        self._write_raw(type + 'J')

    def save_cursor(self):
        self._write_raw('s')

    def restore_cursor(self):
        self._write_raw('u')

    def moveto(self, row, col):
        self._write_raw(row + ';' + col + 'f')


if __name__ == '__main__':
    t = term()
    t.register('y', style(Color16Table.Yellow))
    t.register('m', style(Color16Table.Magenta))
    t.register('hc', style(252, option=Option.UNDERLINE_ON))
    t.register('hcbg', style(252, 100))
    t.register('blink', style(option=Option.BLINK_ON))

    print = t.printr

    print("{y abc {m hallo} welt} {blink B!} {hc abc} {hcbg adf}")
    print()
