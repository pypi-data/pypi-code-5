'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 1, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Widget to hold the options for 
dual lattice and carbon lattice 
minimisation
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
from nanocap.gui.widgets import SpinBox,DoubleSpinBox,HolderWidget,BaseWidget

import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube

from nanocap.core import globals,minimisation,triangulation,minimasearch,structurelog

class CarbonLatticeMinimisationOptions(QtGui.QWidget):
    def __init__(self,structure=None, buttons=False):        
        QtGui.QWidget.__init__(self)
        self.structure = structure
        self.contentlayout = QtGui.QVBoxLayout(self)
        self.contentlayout.setContentsMargins(0,0,0,0)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setLayout(self.contentlayout)
        
        self.holder = BaseWidget(self,group=False,show=True)
        self.contentlayout.addWidget(self.holder)
        
        grid = self.holder.newGrid()
        
        self.FF_type_cb = QtGui.QComboBox()
        self.FF_type_cb.addItem("Unit Radius Topology")
        self.FF_type_cb.addItem("Scaled Topology")
        self.FF_type_cb.addItem("EDIP")
        self.FF_type_cb.addItem("LAMMPS-AREBO")
        self.FF_type_cb.setCurrentIndex(0)
        
        grid.addWidget(QL("Force Field"),0,1)
        grid.addWidget(self.FF_type_cb,0,2,1,3)
        
        self.min_type_cb = QtGui.QComboBox()
        self.min_type_cb.addItem("SD")
        self.min_type_cb.addItem("LBFGS")
        #self.MinTypeCB.addItem("LBFGS-C")
        self.min_type_cb.addItem("MC")
        self.min_type_cb.setCurrentIndex(1)
        
        grid.addWidget(QL("Minimiser"),1,1)
        grid.addWidget(self.min_type_cb,1,2,1,3)
        
        lb = QtGui.QLabel("Steps")
        self.min_steps_entry = SpinBox()
        self.min_steps_entry.setFixedWidth(60)
        self.min_steps_entry.setMaximum(10000000)
        self.min_steps_entry.setValue(100)
        lb2 = QtGui.QLabel("Tol")
        self.min_tol_entry = QtGui.QLineEdit()
        self.min_tol_entry.setText("1e-10")
        self.min_tol_entry.setFixedWidth(60)
        
        grid.addWidget(lb,2,1)
        grid.addWidget(self.min_steps_entry,2,2)
        grid.addWidget(lb2,2,3)
        grid.addWidget(self.min_tol_entry,2,4)
        
        if(buttons):
            
            bt = QtGui.QPushButton("Optimise Scale")
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.optimise_scale)
            grid.addWidget(bt,3,0,1,5)
            
            
            bt = QtGui.QPushButton("Optimise")
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.optimise_structure)
            grid.addWidget(bt,4,0,1,5)
    
    def optimise_scale(self):
        self.optimise_structure(scale=True)
    
    def optimise_structure(self,scale=False):
        FFID = str(self.FF_type_cb.currentText())
        mintol=float(self.min_tol_entry.text())
        minsteps=self.min_steps_entry.value()
        mintype=str(self.min_type_cb.currentText())  

        self.carbon_lattice_minimiser = minimisation.CarbonLatticeMinimiser(FFID=FFID,
                                                                            structure = self.structure)
        self.carbon_lattice_minimiser.mintype = mintype
        self.carbon_lattice_minimiser.ftol=mintol
        self.carbon_lattice_minimiser.minsteps=minsteps
        
        if(scale):
            self.carbon_lattice_minimiser.minimise_scale(self.structure.carbon_lattice)
        else:    
            self.carbon_lattice_minimiser.minimise(self.structure.carbon_lattice,update=False)
        
        self.structure.update_child_structures()
                        
        self.structure.render_update()
        


class DualLatticeMinimisationOptions(QtGui.QWidget):
    def __init__(self,structure=None, buttons=False):        
        QtGui.QWidget.__init__(self)
        self.structure = structure
        self.contentlayout = QtGui.QVBoxLayout(self)
        self.contentlayout.setContentsMargins(0,0,0,0)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setLayout(self.contentlayout)
        
        self.holder = BaseWidget(self,group=False,show=True)
        self.contentlayout.addWidget(self.holder)
        
        grid = self.holder.newGrid()
        
        self.FF_type_cb = QtGui.QComboBox()
        self.FF_type_cb.addItem("Thomson")
        self.FF_type_cb.setCurrentIndex(0)
        
        grid.addWidget(QL("Force Field"),0,1)
        grid.addWidget(self.FF_type_cb,0,2,1,3)
        
        self.min_type_cb = QtGui.QComboBox()
        self.min_type_cb.addItem("SD")
        self.min_type_cb.addItem("LBFGS")
        #self.MinTypeCB.addItem("LBFGS-C")
        self.min_type_cb.addItem("MC")
        self.min_type_cb.setCurrentIndex(1)
        
        grid.addWidget(QL("Minimiser"),1,1)
        grid.addWidget(self.min_type_cb,1,2,1,3)
        
        lb = QtGui.QLabel("Steps")
        self.min_steps_entry = SpinBox()
        self.min_steps_entry.setFixedWidth(60)
        self.min_steps_entry.setMaximum(10000000)
        self.min_steps_entry.setValue(100)
        lb2 = QtGui.QLabel("Tol")
        self.min_tol_entry = QtGui.QLineEdit()
        self.min_tol_entry.setText("1e-10")
        self.min_tol_entry.setFixedWidth(60)
        
        grid.addWidget(lb,2,1)
        grid.addWidget(self.min_steps_entry,2,2)
        grid.addWidget(lb2,2,3)
        grid.addWidget(self.min_tol_entry,2,4)
        
        if(buttons):
            bt = QtGui.QPushButton("Optimise")
            self.connect(bt, QtCore.SIGNAL('clicked()'), self.optimise_structure)
            grid.addWidget(bt,3,0,1,5)


    def optimise_structure(self):
        DualLatticeMinimiser = str(self.FF_type_cb.currentText())
        DualLattice_mintol=float(self.min_tol_entry.text())
        DualLattice_minsteps=self.min_steps_entry.value()
        Dmintype=str(self.min_type_cb.currentText())  

        self.dual_lattice_minimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = self.structure)
        self.dual_lattice_minimiser.mintype = Dmintype
        self.dual_lattice_minimiser.ftol=DualLattice_mintol
        self.dual_lattice_minimiser.minsteps=DualLattice_minsteps 
        self.dual_lattice_minimiser.minimise(self.structure.dual_lattice,update=False)
        
        if(self.structure.type==CAPPEDNANOTUBE):
            self.structure.update_caps()
        
        self.structure.render_update()
            
            
