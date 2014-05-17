#!/usr/bin/env python

try:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets, QtWebKitWidgets
except ImportError:
    from PyQtX import QtCore
    from PyQtX import QtWidgets, QtWebKitWidgets

import os
import sys
import time
import types
from lxml.html import builder as hb
from lxml.html import tostring as html_dumps

from pluzz.pluzz import PluzzMovie, PluzzSearch

TOPBAR_JS="""\
var channels = document.getElementsByClassName("channel");
for (var i=0;i<channels.length; ++i) {
    console.log(channels[i]);
    channels[i].getElementsByTagName('a')[0].onclick = function() {
        qpluzz.select_channel(this.innerHTML);
        return false;
    }
}
var categories = document.getElementsByClassName("category");
for (var i=0;i<categories.length; ++i) {
    categories[i].getElementsByTagName('a')[0].onclick = function() {
        qpluzz.select_category(this.innerHTML);
        return false;
    }
}
"""

SHOWS_JS="""\
var shows = document.getElementsByClassName("show");
for (var i=0;i<shows.length; ++i) {
    shows[i].onclick = function() {
        qpluzz.select_show(this.getAttribute('id'));
        return false;
    }
}
"""

SHOW_JS="""\
document.getElementById("back").onclick = function() {
    qpluzz.goto_list();
    return false;
}
"""

class QVideoView(QtWebKitWidgets.QWebView):
    css_head = hb.LINK(rel="stylesheet", href='file://{}'.format(os.path.join(os.path.dirname(__file__),"resources","pypluzz.css")), type="text/css")
    def __init__(self, *args, verbose=False):
        super(QVideoView, self).__init__(*args)
        self.page().mainFrame().javaScriptWindowObjectCleared.connect(self.handle_slots)
        self.topbar_channels = []
        self.topbar_categories = []
        self.category_selected = "all"
        self.channel_selected = "all"
        self.verbose = verbose

    def handle_slots(self):
        self.page().mainFrame().addToJavaScriptWindowObject("qpluzz", self);

    def setup_topbar(self):
        if len(self.topbar_channels) == 0 or len(self.topbar_categories) == 0:
            with PluzzSearch(verbose=True) as s:
                try:
                    cat_l = [hb.LI(hb.CLASS("category"),
                                    hb.A(c, href="javascript:void(0)")) for c in s.get_categories()]
                    chn_l = [hb.LI(hb.CLASS("channel"),
                                    hb.A(c, href="javascript:void(0)")) for c in s.get_channels()]
                    self.topbar_channels = hb.UL(*(chn_l), id='channels')
                    self.topbar_categories = hb.UL(*(cat_l), id='categories')
                except Exception as err:
                    if self.verbose:
                        import traceback
                        traceback.print_exc()

    def build_show_list(self, **args):
        self.setup_topbar()
        with PluzzSearch(verbose=True) as s:
            try:
                shw_l = [hb.DIV(hb.CLASS("image"),
                                hb.A(hb.CLASS("show"),
                                     hb.IMG(src=md['image'],
                                            alt=md['title']),
                                     hb.DIV(hb.CLASS('caption'),
                                            hb.P(hb.CLASS('caption_content'),
                                                 md['title'])),
                                     id=md['id'], href="javascript:void(0)")) for md in s.list(**args)]
            except Exception as err:
                shw_l = [str(err)]
                if self.verbose:
                    import traceback
                    traceback.print_exc()

        doc = hb.HTML(hb.HEAD(self.css_head),
                      hb.BODY(hb.DIV(hb.CLASS('header'),
                                     self.topbar_channels,
                                     self.topbar_categories),
                              hb.DIV(hb.CLASS('content'),
                                     hb.UL(*(shw_l)))
                              )
                      )
        self.setHtml(html_dumps(doc).decode('utf8'))
        self.settings().setUserStyleSheetUrl(QtCore.QUrl(os.path.join(os.path.dirname(__file__),"resources","pypluzz.css")))
        self.page().mainFrame().evaluateJavaScript(TOPBAR_JS)
        self.page().mainFrame().evaluateJavaScript(SHOWS_JS)

    def build_show_data(self, i):
        self.setup_topbar()
        with PluzzMovie(i) as m:
            try:
                t_when = time.strftime(_("On %d %h %Y at %H:%M"), time.localtime(m['diffusion']['timestamp']))
                # t_until = time.strftime(_("On %d %h %Y at %H:%M"), time.localtime(m['diffusion']['???']))
                show_md = [hb.H1(_("Summary of the show '{}'").format(m['titre'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Id'))       , hb.SPAN(hb.CLASS('md_val'), m['id'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('AEDRA'))    , hb.SPAN(hb.CLASS('md_val'), m['id_aedra'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Broadcast')), hb.SPAN(hb.CLASS('md_val'), t_when)),
                        #hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Until'))   , hb.SPAN(hb.CLASS('md_val'), t_until)),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Length'))   , hb.SPAN(hb.CLASS('md_val'), m['duree'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Genre'))    , hb.SPAN(hb.CLASS('md_val'), m['genre'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Season'))   , hb.SPAN(hb.CLASS('md_val'), str(m['saison']))),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Website'))  , hb.SPAN(hb.CLASS('md_val'), m['url_site'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Pluzz'))    , hb.SPAN(hb.CLASS('md_val'), m['url_reference'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Channel'))  , hb.SPAN(hb.CLASS('md_val'), m['chaine'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Picture'))  , hb.IMG(hb.CLASS('md_val'), src="http://pluzz.francetv.fr"+m['image'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Rights'))   , hb.SPAN(hb.CLASS('md_val'), m['droit']['csa'])),
                        hb.DIV(hb.SPAN(hb.CLASS('md_key'), _('Crew'))     ,
                                hb.UL(hb.CLASS('crew_list'),
                                        *([hb.LI(", ".join(p['fonctions']), ':', p['prenom'], p['nom']) for p in m['personnes']])
                                        )
                                ),
                        hb.DIV(hb.CLASS('synopsis'), m['synopsis'])
                        ]
            except Exception as err:
                show_md = [str(err)]
                if self.verbose:
                    import traceback
                    traceback.print_exc()

        doc = hb.HTML(hb.HEAD(self.css_head),
                      hb.BODY(hb.DIV(hb.A('X', href="javascript:void(0)"), id='back'),
                              hb.DIV(hb.CLASS('header'),
                                     self.topbar_channels,
                                     self.topbar_categories),
                              hb.DIV(hb.CLASS('content'),
                                     hb.UL(*(show_md)))
                              )
                      )

        self.setHtml(html_dumps(doc).decode('utf8'))
        self.settings().setUserStyleSheetUrl(QtCore.QUrl(os.path.join(os.path.dirname(__file__),"resources","pypluzz.css")))
        self.page().mainFrame().evaluateJavaScript(TOPBAR_JS)
        self.page().mainFrame().evaluateJavaScript(SHOW_JS)

    @QtCore.pyqtSlot()
    def goto_list(self):
        self.parent().url_txt.setText('')
        self.parent().start_btn.setEnabled(False)
        self.build_show_list(channel=self.channel_selected,
                             category=self.category_selected,
                             limit=100, sort="alpha")

    @QtCore.pyqtSlot("QString")
    def select_show(self, i):
        self.parent().url_txt.setText(i)
        self.parent().start_btn.setEnabled(True)
        self.build_show_data(i)

    @QtCore.pyqtSlot("QString")
    def select_category(self, i):
        self.category_selected = i
        self.build_show_list(channel=self.channel_selected,
                             category=self.category_selected,
                             limit=100, sort="alpha")

    @QtCore.pyqtSlot("QString")
    def select_channel(self, i):
        self.channel_selected = i
        self.build_show_list(channel=self.channel_selected,
                             category=self.category_selected,
                             limit=100, sort="alpha")

class QPluzz(QtWidgets.QWidget):

    update_progress_bar = QtCore.pyqtSignal(int)
    update_eta_text = QtCore.pyqtSignal(str)

    def __init__(self, args):
        super(QPluzz, self).__init__()

        self.defaults = args

        # row #0
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel(_('Pluzz Movie Downloader')))
        # row #1
        self.web_view = QVideoView(self, verbose=args['--verbose'])
        self.web_view.build_show_list(limit=100, sort="alpha")
        vbox.addWidget(self.web_view)
        # row #2
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(QtWidgets.QLabel(_('URL of movie to load')))
        self.url_txt = QtWidgets.QLineEdit()
        self.url_txt.setText(args['<id>'])
        hbox.addWidget(self.url_txt)
        vbox.addLayout(hbox)
        # row #3
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(QtWidgets.QLabel(_('Directory where to download')))
        self.path_txt = QtWidgets.QLineEdit()
        self.path_txt.setText(args['--target'])
        hbox.addWidget(self.path_txt)
        vbox.addLayout(hbox)
        # row #4
        hbox = QtWidgets.QHBoxLayout()
        self.eta = QtWidgets.QLabel('')
        self.update_eta_text.connect(self.eta.setText)
        hbox.addWidget(self.eta)
        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        self.pbar.setTextVisible(True)
        self.update_progress_bar.connect(self.pbar.setValue)
        hbox.addWidget(self.pbar, stretch=1)
        vbox.addLayout(hbox)
        # row #5
        self.start_btn = QtWidgets.QPushButton(_('Start Download!'))
        self.start_btn.clicked.connect(self.on_click_start)
        if args['<id>']:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
        vbox.addWidget(self.start_btn)
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle(_('Pluzz Movie loader'))
        self.show()

    @QtCore.pyqtSlot()
    def on_click_start(self):
        def update_progress(position, total, spent, start):
            eta = int((time.time() - start)*total/position)
            adv = position/total
            if self.defaults['--verbose']:
                print("{: >10}/{: <10} : {: >3}s/{: <3}s".format(position, total, spent, eta), end='\r')
            self.update_eta_text.emit("ETA {}s/{}s".format(spent, eta))
            self.update_progress_bar.emit(adv*100)

        def dl(that):
            self.start_btn.setDisabled(True)
            movie.save(callback=update_progress, avconv_path=self.defaults['--avconv'], verbose=self.defaults['--verbose'])
            self.update_eta_text.emit("ETA -/-")
            self.update_progress_bar.emit(0)
            self.start_btn.setEnabled(True)

        with PluzzMovie(self.url_txt.text()) as movie:
            t = QtCore.QThread(self)
            # Monkey patching of QThread to change the run function!
            t.run = types.MethodType(dl, t)
            t.start()

def main(args):
    app = QtWidgets.QApplication(sys.argv)
    qpluzz = QPluzz(args)
    sys.exit(app.exec_())

