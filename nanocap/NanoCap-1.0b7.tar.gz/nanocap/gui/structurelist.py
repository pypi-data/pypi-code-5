'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 14, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

List of current structures,

on click show structures renderwindow and 
options window


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

import os,time,platform,random,math,copy
from nanocap.core.globals import *
from nanocap.gui.settings import * 
from nanocap.gui.common import *
from nanocap.core.util import *
from nanocap.rendering import vtkqtrenderwidgets

class StructureList(QtGui.QListWidget):
    def __init__(self,gui):
        QtGui.QListWidget.__init__(self)
        self.setStyleSheet("font: "+str(font_size+2)+"pt")
        self.gui = gui
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.structures = []    
        
        self.connect(self,QtCore.SIGNAL('clicked (QModelIndex)'), self.selectStructure) 
        
        self.gui.exportStructureWindow.export_structure.connect(self.exportCurrentStructure)
        self.gui.loadFromFileWindow.load_structure.connect(self.loadFromFileWindow)
        
        self.setMaximumHeight(120)
    
    def loadFromFileWindow(self):
        self.addStructure(self.gui.loadFromFileWindow.structure)
    
    def exportCurrentStructure(self,argdict):
        index = self.currentIndex()
        if(index.row()<0):return
        
        structure = self.structures[index.row()] 
        
        structure.export(**argdict)
        
        printl(argdict,structure)      
        
    
    def selectStructure(self,index):
        self.showStructure(index.row())
        
    def updateList(self):
        printl("in updateList")
        for i in range(0,self.count()):
            self.item(i).setText(self.structures[i].get_GUI_description())
    
    def showStructure(self,i):
        printl( "Showing structure",i)
  
        for structure in self.structures:
            structure.hide()
        
        self.structures[i].show()
        
    
    def addStructure(self,structure=None):
        printl("adding structure",structure.type.label)
        
        structure.render(render_window_holder = self.gui.mdilayout,
                         options_holder = self.gui.dock.toolbar.MainWidget,show=False)
        
        self.structures.append(structure)
        
        if(structure!=None):
            description = structure.get_GUI_description()
            item = QtGui.QListWidgetItem(description)
            self.addItem(item)
            self.setCurrentItem(item)
        
        printl("update_structure",structure.type.label)
        self.connect(structure.options_window,QtCore.SIGNAL('update_structure()'), self.updateList) 

        structure.render_window.vtkframe.centerCameraOnPointSet(structure.carbon_lattice)
        
        self.showStructure(-1)
        
    def sizeHint(self):
        return QtCore.QSize(400,200) 