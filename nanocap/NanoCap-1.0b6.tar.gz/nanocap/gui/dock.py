'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Dock widget to hold toolbars

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
import os,sys,math,copy,random
import numpy

from nanocap.core.globals import *
from nanocap.core.util import *
from nanocap.gui.settings import *
from nanocap.gui.widgets import BaseWidget,HolderWidget
import nanocap.gui.toolbar as toolbar
from nanocap.gui import menubar

class dock(QtGui.QDockWidget):    
    def __init__(self, Gui, MainWindow, width, height, title):
        QtGui.QDockWidget.__init__(self, None)
                
        self.MainWindow = MainWindow
        self.Gui = Gui
        self.setTitleBarWidget(QtGui.QWidget())
        self.holder = BaseWidget(h=0,w=n_DOCKWIDTH,align=QtCore.Qt.AlignTop)
        self.holder.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)

        self.MenuBar = menubar.MenuBar(self)        
        self.holder.addWidget(self.MenuBar,align=QtCore.Qt.AlignTop)
        
        self.connect(self.MenuBar,QtCore.SIGNAL('new_structure_search()'), self.Gui.structureGenWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('new_single_structure()'), self.Gui.singleStructureGenWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('load_from_local()'), self.Gui.dataBaseViewerWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('export_structure()'), self.Gui.exportStructureWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('show_preferences()'), self.Gui.preferencesWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('show_local_database()'), self.Gui.dataBaseViewerWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('load_from_file()'), self.Gui.loadFromFileWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('show_about()'), self.Gui.aboutWindow.bringToFront)
        self.connect(self.MenuBar,QtCore.SIGNAL('show_help()'), self.Gui.helpWindow.bringToFront)
        
        self.setWidget(self.holder)
    
    def sizeHint(self):
        return QtCore.QSize(n_DOCKWIDTH,n_DOCKHEIGHT)

    def draw(self):
        self.toolbar = toolbar.toolbar(self.Gui, self.MainWindow)
        self.holder.addWidget(self.toolbar)
        
        self.iconWidget = QtGui.QLabel()
        self.iconWidget.setStyleSheet("QWidget {background-color: white}")
        self.icon = QtGui.QPixmap(str(IconDir) + 'Logo6BlackGrey.png')
        #self.icon = self.icon.scaledToWidth(self.width())
        self.iconWidget.setPixmap(self.icon)
        self.iconWidget.setGeometry(0, 0, self.width(), 55)
         
        self.holder.addWidget(self.iconWidget)
        self.holder.layout.setAlignment(self.iconWidget, QtCore.Qt.AlignRight)
        
        self.holder.show()
