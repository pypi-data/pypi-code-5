'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 13, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

NanoCap help window.

Needs to interface with a static
help doc

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy
from nanocap.core.util import *
from nanocap.core import minimisation,triangulation,minimasearch,structurelog

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget,Frame
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube



class HelpWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setWindowTitle("Help")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(5)
        #self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.contentlayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.contentlayout)
        
        self.topic = ['Fullerenes','Nanotubes','Capped Nanotubes','Optimisation',
                      'Documentation']
        
        self.options_holder = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)
        self.options = {}
        
        self.options_list = QtGui.QListWidget()
        for topic in self.topic:
            self.options_list.addItem(topic)
            self.options[topic] = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)
            self.options_holder.addWidget(self.options[topic],align = QtCore.Qt.AlignTop)

        self.options_list.setFixedWidth(140)
        self.connect(self.options_list,QtCore.SIGNAL('clicked (QModelIndex)'), self.option_changed) 
        
        self.contentlayout.addWidget(self.options_list,0,0)
        self.contentlayout.addWidget(self.options_holder,0,1)
        
        
        #for form in self.options.values():form.hide()
        for form in self.options.values():form.hide()
        
        self.setup_pages()
        
    def setup_pages(self):
        
        topic = 'Documentation'
        
        self.pub_group = BaseWidget(self,group=True,title="Publications",show=True,align = QtCore.Qt.AlignTop)
        
        self.pub_group = QTextEdit()
        self.pub_group.setReadOnly(True) 
        
        
        #self.pub_group.
        
        #self.pub_group.addWidget(QL("Generalized method for constructing the atomic coordinates of nanotube caps",
        #                      link = "http://journals.aps.org/prb/abstract/10.1103/PhysRevB.87.155430"))
        
        #http://journals.aps.org/prb/abstract/10.1103/PhysRevB.87.155430
        
        self.options[topic].addWidget(self.pub_group)
        
        
        
        
    def option_changed(self,index):
        option = self.options_list.currentItem().text()
        for form in self.options.values():form.hide()
        
        self.options[option].show()
        
    def sizeHint(self):
        return QtCore.QSize(500,400) 
            
    def bringToFront(self):
        self.raise_()
        self.show()    