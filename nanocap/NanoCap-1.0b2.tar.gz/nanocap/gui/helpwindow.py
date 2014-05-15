'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 13, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

NanoCap help window.

Current uses the reStructuredText
in the nanocap.help directory.

This needs to be link with online 
docs... 

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types,glob,re
import docutils.core as core
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
        
        
        '''
        only use the .tex derived html files. there's a problem with bundling
        docutils with py2app (outdated recipe?) so cannot use 
        core.publish_string
        '''
        
        files = glob.glob(get_root()+"/help/*.txt")
        printl("files",files,get_root()+"/help")
        self.topic =[ re.sub(r"(\w)([A-Z])", r"\1 \2", os.path.basename(file).split(".")[0]) for file in files]
        
        
        #let's have general at the top and documentation a the end
        try:self.topic.insert(0, self.topic.pop(self.topic.index('General')))
        except:pass
        try:self.topic.append(self.topic.pop(self.topic.index('Documentation')))
        except:pass
        
        self.options_holder = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)
#         self.options = {}
#         self.text_edit = {}
#         
#         self.options_list = QtGui.QListWidget()
#         for topic in self.topic:
#             self.options_list.addItem(topic)
#             self.options[topic] = BaseWidget(self,group=False,show=True,align = QtCore.Qt.AlignTop)
#             #self.options_holder.addWidget(self.options[topic],align = QtCore.Qt.AlignTop)
#             self.text_edit[topic] = QtGui.QTextBrowser()
#             self.text_edit[topic].setReadOnly(True) 
#             self.text_edit[topic].setOpenExternalLinks(True)
#             file = topic.replace(" ","")
#             #print file,topic,topic.strip()
#             print("help files",get_root()+"/help/")
#             try:
#                 lines = open(get_root()+"/help/"+file+"/index.html","r").read()
#                 self.text_edit[topic].setSearchPaths([get_root()+"/help/"+file+"/",])
#                 self.text_edit[topic].insertHtml(lines)
#             except:
#                 try:
#                     lines = open(get_root()+"/help/"+file+".html","r").read()
#                     self.text_edit[topic].insertHtml(lines)
#                 except:
#                     lines = open(get_root()+"/help/"+file+".txt","r").read()
#                     
#                 #self.text_edit[topic].setText(core.publish_string(lines,writer_name='html'))
#             
#             self.options[topic].addWidget(self.text_edit[topic])
#             
# 
#         self.options_list.setFixedWidth(140)
#         self.connect(self.options_list,QtCore.SIGNAL('clicked (QModelIndex)'), self.option_changed) 
#         
        #self.contentlayout.addWidget(self.options_list,0,0)
        self.text_edit = QtGui.QTextBrowser()
        self.text_edit.setReadOnly(True) 
        self.text_edit.setOpenExternalLinks(True)
        self.text_edit.setSearchPaths([get_root()+"/help/Doc/",])
        lines = open(get_root()+"/help/Doc/index.html","r").read()
        self.text_edit.insertHtml(lines)
        
        
        self.options_holder.addWidget(self.text_edit,align = QtCore.Qt.AlignTop)
        self.contentlayout.addWidget(self.options_holder,0,1)

        #for form in self.options.values():form.hide()

    def option_changed(self,index):
        option = self.options_list.currentItem().text()
        for form in self.options.values():form.hide()
        
        self.options[option].show()
        
    def sizeHint(self):
        return QtCore.QSize(750,400) 
            
    def bringToFront(self):
        self.raise_()
        self.show()    