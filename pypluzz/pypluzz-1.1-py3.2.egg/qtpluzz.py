#!/usr/bin/env python

try:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
except ImportError:
    from PyQtX import QtCore
    from PyQtX import QtWidgets

import sys
import types

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
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(QtWidgets.QLabel(_('URL of movie to load')))
        self.url_txt = QtWidgets.QLineEdit()
        self.url_txt.setText(args['<url>'])
        hbox.addWidget(self.url_txt)
        vbox.addLayout(hbox)
        # row #2
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(QtWidgets.QLabel(_('Directory where to download')))
        self.path_txt = QtWidgets.QLineEdit()
        self.path_txt.setText(args['--target'])
        hbox.addWidget(self.path_txt)
        vbox.addLayout(hbox)
        # row #3
        hbox = QtWidgets.QHBoxLayout()
        self.eta = QtWidgets.QLabel(_('ETA -/-'))
        self.update_eta_text.connect(self.eta.setText)
        hbox.addWidget(self.eta)
        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        self.pbar.setTextVisible(True)
        self.update_progress_bar.connect(self.pbar.setValue)
        hbox.addWidget(self.pbar, stretch=1)
        vbox.addLayout(hbox)
        # row #4
        self.start_btn = QtWidgets.QPushButton(_('Start Download!'))
        self.start_btn.clicked.connect(self.on_click_start)
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
            # print("{: >10}/{: <10} : {: >3}s/{: <3}s".format(position, total, spent, eta), end='\r')
            self.update_eta_text.emit("ETA {}s/{}s".format(spent, eta))
            self.update_progress_bar.emit(adv*100)

        def dl(that):
            self.start_btn.setDisabled(True)
            movie.save(callback=update_progress, avconv_path=self.defaults['--avconv'], verbose=args['--verbose'])
            self.update_eta_text.emit("ETA -/-")
            self.update_progress_bar.emit(0)
            self.start_btn.setEnabled(True)

        movie = PluzzMovie(self.url_txt.text())
        movie.retrieve_data()
        t = QtCore.QThread(self)
        # Monkey patching of QThread to change the run function!
        t.run = types.MethodType(dl, t)
        t.start()

def main(args):
    app = QtWidgets.QApplication(sys.argv)
    qpluzz = QPluzz(args)
    sys.exit(app.exec_())

