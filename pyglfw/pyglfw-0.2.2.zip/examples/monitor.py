# coding=utf-8

import pyglfw.pyglfw as fw

def scrawl():
    fw.init()

    monitors = fw.get_monitors()

    def make_window(i, moni):
        w, h = 800, 600
        return fw.Window(w, h, 'MONITOR%i' % i)

    wnds = [ make_window(i, moni) for i, moni in enumerate(monitors) ]

    while not any([ w.should_close for w in wnds ]):

        for w in wnds:
            w.swap_buffers()
            if w.keys.escape:
                print(w)

        fw.poll_events()

    fw.terminate()

