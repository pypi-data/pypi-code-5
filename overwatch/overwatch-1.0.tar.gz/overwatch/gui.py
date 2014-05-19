import os
import pkg_resources
import sys
import logging
from threading import Thread
import time
import re
import math
import datetime
from server import Server

log = logging.getLogger('root')

#DIR = os.path.dirname(__file__)


get_resource_path = lambda filename: pkg_resources.resource_filename('overwatch', os.path.join('data', filename))

try:
    import pygtk
    pygtk.require('2.0')
except:
    pass
try:
    import gtk
    import gtk.glade
    import gobject
    import pango
    gobject.threads_init()
except Exception, e:
    log.error('Could not load GTK libs, error was: %s' % e)
    raise e
    sys.exit(1)

'''gtk.window_set_default_icon_list(
    gtk.gdk.pixbuf_new_from_file('images/icon256.png'),
    gtk.gdk.pixbuf_new_from_file('images/icon128.png'),
    gtk.gdk.pixbuf_new_from_file('images/icon64.png'),
    gtk.gdk.pixbuf_new_from_file('images/icon48.png'),
    gtk.gdk.pixbuf_new_from_file('images/icon32.png'),
    gtk.gdk.pixbuf_new_from_file('images/icon16.png'),
)'''


def defer(method, *args):
    gobject.idle_add(method, *args)


def deferred(fn):
    def wrapper(self, *args, **kwargs):
        defer(fn, *[self] + list(args))
    return wrapper


class Form:
    '''
    Generic form class.
    Loads a form ant initializes main widget.
    '''
    def __init__(self, gui, form_id):
        ''' Load form, connect signals. '''
        self.glade = gtk.Builder()
        f = open(get_resource_path('%s.glade' % (form_id)), 'r')
        xml = f.read().replace('GtkBox" id="h', 'GtkHBox" id="h').replace('GtkBox" id="v', 'GtkVBox" id="v')
        xml = '\n'.join([line for line in xml.split('\n') if line.find('requires') < 0])
        f.close()
        self.glade.add_from_string(xml)
        self.window = self.glade.get_object(form_id)
        self.gui = gui
        self.glade.connect_signals(self)

    def show(self):
        ''' Show form. '''
        self.window.show()

    def __getattr__(self, name):
        ''' Delegates unexisting properties to parent GUI object. '''
        if name.startswith('id_'):
            widget_matches = [x for x in self.glade.get_objects() if isinstance(x, (gtk.Buildable, gtk.ListStore)) and gtk.Buildable.get_name(x) == name[3:]]
            if len(widget_matches):
                return widget_matches[0]
        elif name.endswith('_cb'):
            def delegate_event(*args):
                self.gui.on_event(name, args)
            return delegate_event
        else:
            raise AttributeError('Attribute \'%s\' not found in Form (or its derivatives).' % name)


class MainForm(Form):
    '''
    Main form.
    '''

    def __init__(self, gui):
        ''' Inits main window with map, skills, chat etc. '''
        # Call parent constructor in order to properly create form.
        Form.__init__(self, gui, 'form')
        self.window.maximize()
        self.window.connect('destroy', gtk.main_quit)

        self.log_items_filter = self.id_log_items_store.filter_new()
        self.log_items_filter.set_visible_column(14)
        self.id_log_items_tree.set_model(self.log_items_filter)

        self.id_log_items_filter_entry.connect('changed', self.on_filter_change)

    def on_filter_change(self, entry):
        store = self.id_log_items_store
        text = entry.get_text().lower()
        for row in store:
            matched = False
            for i in (1, 5, 9):
                if row[i].lower().find(text) != -1:
                    matched = True
            row[14] = matched

class GUI:
    LEVEL_COLORS = {
        'DEBUG': (gtk.gdk.color_parse('#AAFFFF'), gtk.gdk.color_parse('#007777')),
        'INFO': (gtk.gdk.color_parse('#00AA00'), gtk.gdk.color_parse('#FFFFFF')),
        'WARNING': (gtk.gdk.color_parse('#AAAA00'), gtk.gdk.color_parse('#FFFFFF')),
        'ERROR': (gtk.gdk.color_parse('#AA0000'), gtk.gdk.color_parse('#FFFFFF')),
        'EXCEPTION': (gtk.gdk.color_parse('#AA0000'), gtk.gdk.color_parse('#FFFFFF')),
    }

    CRC_COLORS = {
        0: gtk.gdk.color_parse('#AA7777'),
        1: gtk.gdk.color_parse('#77AA77'),
        2: gtk.gdk.color_parse('#7777AA'),
        3: gtk.gdk.color_parse('#AA0077'),
        4: gtk.gdk.color_parse('#AA7700'),
        5: gtk.gdk.color_parse('#00AA77'),
        6: gtk.gdk.color_parse('#77AA00'),
        7: gtk.gdk.color_parse('#0077AA'),
        8: gtk.gdk.color_parse('#7700AA'),
        9: gtk.gdk.color_parse('#AA0000'),
        10: gtk.gdk.color_parse('#00AA00'),
        11: gtk.gdk.color_parse('#0000AA'),
        12: gtk.gdk.color_parse('#00AAAA'),
        13: gtk.gdk.color_parse('#AA00AA'),
        14: gtk.gdk.color_parse('#AAAA00'),
        15: gtk.gdk.color_parse('#77AAAA'),
        16: gtk.gdk.color_parse('#AA77AA'),
    }

    def __init__(self):
        self.main_form = MainForm(self)
        self.main_form.show()

        self.i = 0

        self.server = Server(self)
        self.server.start()

    def crc(self, s):
        return sum([ord(x) for x in s]) % len(GUI.CRC_COLORS)

    @deferred
    def on_log_event(self, project_id, record):
        self.i += 1
        msg_formatted = record.get('msg').replace('<', '&lt;').replace('>', '&gt;')
        msg_formatted = re.sub('File (.*), line ([\d]+), in (.*)', 'File <span foreground="#0055AA">\\1</span>, line <span foreground="#AA0000">\\2</span>, in <span foreground="#AA0000">\\1</span>', msg_formatted)
        msg_formatted = re.sub('\&lt\;(.*)\&gt\;', '<span foreground="#FF1177" weight="bold">&lt;\\1&gt;</span>', msg_formatted)
        msg_formatted = re.sub('\{([^\{]*)\}', '<span foreground="#00AAFF" weight="bold">{\\1}</span>', msg_formatted)
        self.main_form.id_log_items_store.append([
            self.i,
            #'<span foreground="#FFFFFF" background="#00AA00">%s</span>' % project_id,
            project_id,
            record.get('levelname'),
            int(record.get('levelno')),
            record.get('source'),
            record.get('module'),
            record.get('filename'),
            record.get('func_name'),
            int(record.get('lineno')),
            msg_formatted,
            datetime.datetime.fromtimestamp(float(record.get('time'))).strftime('%H:%M:%S'),
            GUI.LEVEL_COLORS[record.get('levelname')][0],
            GUI.LEVEL_COLORS[record.get('levelname')][1],
            GUI.CRC_COLORS[self.crc(project_id)],
            True,
        ])

        tree = self.main_form.id_log_items_tree
        tree.set_cursor_on_cell((len(self.main_form.log_items_filter),))

    @deferred
    def on_new_project(self, project_id, pid):
        self.main_form.id_projects_store.append([project_id, pid, GUI.CRC_COLORS[self.crc(project_id)]])

    @deferred
    def on_remove_project(self, project_id, pid):
        store = self.main_form.id_projects_store
        for row in store:
            if row[1] == pid:
                store.remove(row.iter)

    def main(self):
        gtk.main()
