#!/usr/bin/env python
import curses
from curses import panel

W, H = 80, 24

def init_scr():
    ''' Initialize curses screen '''
    scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    scr.keypad(1)
    return scr

def term_scr(scr):
    ''' Clean up curses '''
    curses.nocbreak()
    scr.keypad(0)
    curses.echo()
    curses.endwin()

def create_game_win():
    ''' Create game window '''
    win = curses.newwin(H, W, 0, 0)
    win.border(1)
    return win

def write_str(win, x, y, s):
    ''' Write string at pos in window '''
    win.addstr(y, x, s)

def title_str(win, s):
    ''' Write string in title of window '''
    x = (W / 2) - (len(s) / 2)
    write_str(win, x, 0, s)

def ckey(char):
    if len(char) > 1:
        getattr(curses, 'KEY_%s' % char)
    return ord(char)

def show_menu(win, items):
    ''' Draw menu with items
    items: (char, string)
    '''
    chars, _ = zip(*items)
    keys = {ckey(x): x for x in chars}
    pan = panel.new_panel(win)
    pan.hide()
    panel.update_panels()
    pan.top()
    pan.show()
    i = 1
    for char, item in items:
        msg = '%s - %s' % (char, item)
        win.addstr(i, 1, msg, curses.A_NORMAL)
        i += 1
    ch = None
    while ch not in keys:
        ch = win.getch()
    pan.hide()
    win.clear()
    panel.update_panels()
    curses.doupdate()
    return keys[ch]
        

def main():
    scr = init_scr()
    win = create_game_win()
    title_str(win, 'The Cursed Lich!')
    win.refresh()
    ch = show_menu(win, [
        ('j', 'Join official server'),
        ('3', 'Join third party server'),
        ('t', 'Tutorial'),
        ('h', 'Help'),
        ('q', 'Quit'),
    ])
    if ch == 'q':
        write_str(win, 5, 5, 'You quitter!')
    win.refresh()
    import time ; time.sleep(1)
    term_scr(scr)

if __name__ == '__main__':
    main()

