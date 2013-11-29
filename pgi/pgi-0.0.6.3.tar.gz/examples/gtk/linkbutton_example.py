#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2011 Sebastian Pölsterl
#
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

import sys
sys.path.insert(0, '../..')
import pgi
pgi.install_as_gi()

from gi.repository import Gtk

class LinkButtonWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="LinkButton Demo")
        self.set_border_width(10)

        button = Gtk.LinkButton("http://www.gtk.org", "Visit GTK+ Homepage")
        self.add(button)

win = LinkButtonWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
