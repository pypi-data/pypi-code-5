'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: May 7, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Window to view the current status of 
a database


-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''


from nanocap.core.globals import *
import os,sys,math,copy,random,time,threading,Queue,types,re
import numpy

from nanocap.gui.settings import *
from nanocap.gui.common import *
from nanocap.core.util import *
import nanocap.gui.structuretable as structuretable
import nanocap.gui.progresswidget as progresswidget
import nanocap.gui.structureinputoptions as structureinputoptions
import nanocap.gui.minimiserinputoptions as minimiserinputoptions 

from nanocap.gui.frozencoltablewidget import FrozenTableWidget
from nanocap.gui.tablebuttondelegate import  TableItemDelegate
from nanocap.gui.widgets import BaseWidget,HolderWidget

from nanocap.structures import fullerene
from nanocap.structures import cappednanotube

from nanocap.core import minimisation,triangulation,minimasearch,structurelog

from nanocap.db import database

class DataBaseTable(QtGui.QWidget):
    def __init__(self,database):
        QtGui.QWidget.__init__(self)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Expanding)
        
        self.database = database     
        self.general_table = FrozenTableWidget(NFrozen=1,
                                             DelegateIcons=[[0,1,'view_1.png'],
                                                            ]
                                             )
        self.general_table.frozenTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.general_table.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        
        self.users_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
                
        self.dual_lattice_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
        self.carbon_lattice_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )

        self.rings_table = FrozenTableWidget(NFrozen=0,
                                             DelegateIcons=[]
                                             )
        
        self.general_table.setStretchLastSection(True)
        self.users_table.setStretchLastSection(False)
        self.dual_lattice_table.setStretchLastSection(False)
        self.carbon_lattice_table.setStretchLastSection(False)
        self.rings_table.setStretchLastSection(False)
        self.general_table.setMinimumWidth(0)
        
        self.general_table.setHeaders(["View",])
        
        headers = []
        for field in self.database.fields['users']:headers.append(field.__repr__())      
        self.users_table.setHeaders(headers)
        headers = []
        for field in self.database.fields['dual_lattices']:headers.append(field.__repr__())      
        self.dual_lattice_table.setHeaders(headers)
        headers = []
        for field in self.database.fields['carbon_lattices']:headers.append(field.__repr__())      
        self.carbon_lattice_table.setHeaders(headers)
        headers = []
        for field in self.database.fields['rings']:headers.append(field.__repr__())      
        self.rings_table.setHeaders(headers)
           
                
        self.contentlayout = QtGui.QGridLayout(self)
        self.contentlayout.setContentsMargins(5,5,5,5)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.setLayout(self.contentlayout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(HolderWidget([QL("",font="bold ",align=QtCore.Qt.AlignCenter),self.general_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("User",font="bold ",align=QtCore.Qt.AlignCenter),self.users_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Dual Lattice",font="bold ",align=QtCore.Qt.AlignCenter),self.dual_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Carbon Lattice",font="bold",align=QtCore.Qt.AlignCenter),self.carbon_lattice_table],stack="V"))
        self.splitter.addWidget(HolderWidget([QL("Rings",font="bold ",align=QtCore.Qt.AlignCenter),self.rings_table],stack="V"))
        self.splitter.setHandleWidth(1)
        self.contentlayout.addWidget(self.splitter,0,0)
        
        self.general_table.setMinimumWidth(self.general_table.sizeHint().width()) 
        
        self.general_table.link_table(self.users_table)
        self.users_table.link_table(self.dual_lattice_table)
        self.dual_lattice_table.link_table(self.carbon_lattice_table)
        self.carbon_lattice_table.link_table(self.rings_table)
         
        self.connect(self.general_table,QtCore.SIGNAL("delegatePressed(QModelIndex)"),self.viewStructure)
        
        self.show()
        
    def clear(self):
        self.carbon_lattice_table.reset()   
        self.rings_table.reset()   
        self.general_table.reset()   
        self.dual_lattice_table.reset()   
        self.users_table.reset()   
        
    def populate(self,search_params,orderby,order):
        self.user_ids=[]
        self.dual_lattice_ids=[]
        self.carbon_lattice_ids=[]
        
        args = []
        for key,val in search_params.items():
            
             p = re.compile('[<=>]')
             a =p.findall(str(val))
             printl(a)
             if(len(a)==0):
                 operator="="
                 comp = val
             else:
                 operator="".join(a)
                 comp = val
                 for ai in a: comp=comp.replace(str(ai)," ")
             
             args.append(key+operator+"'"+str(comp)+"'")
             
        if(len(args)==0):wherestring=""
        else:wherestring = "where " + ' and '.join(args)
        printl("wherestring",wherestring)
        
        sort_string = "order by {} {}".format(orderby,order)
        
        query = '''
        select users.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        
        #where dual_lattices.type='Fullerene' or dual_lattices.type='Capped Nanotube';
        
        out = self.database.query(query)
        for row in out:
            self.users_table.addRow(row)
            self.user_ids.append(row[self.database.get_field_column('users','id')]) 
            
        query = '''
        select dual_lattices.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        out = self.database.query(query)
        for row in out:
            printl(row)
            self.dual_lattice_table.addRow(row)
            self.dual_lattice_ids.append(row[self.database.get_field_column('dual_lattices','id')]) 
        
        query = '''
        select carbon_lattices.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        out = self.database.query(query)
        for row in out:
            self.carbon_lattice_table.addRow(row)
            self.carbon_lattice_ids.append(row[self.database.get_field_column('carbon_lattices','id')]) 
        query = '''
        select rings.*
        from users 
        inner join dual_lattices on dual_lattices.user_id=users.id 
        left outer join carbon_lattices on carbon_lattices.dual_lattice_id=dual_lattices.id
        left outer join rings on rings.dual_lattice_id=dual_lattices.id
        '''+wherestring+" "+sort_string + ";"
        out = self.database.query(query)
        for row in out:
            self.rings_table.addRow(row)
        #print out
        for row in out:
            self.general_table.addRow(["null",])
        
         
    def viewStructure(self,index):
        col,row = index.column(),index.row()
        self.emit(QtCore.SIGNAL("viewStructure(int)"),row)    
      
    def sizeHint(self):
 
        return QtCore.QSize(1200,500)
    
class DataBaseViewerWindow(QtGui.QWidget):
    def __init__(self,Gui,MainWindow,ThreadManager):
        self.Gui = Gui
        self.MainWindow = MainWindow
        self.ThreadManager = ThreadManager
        QtGui.QWidget.__init__(self,self.MainWindow,QtCore.Qt.Window)
        
        self.setWindowTitle("Database Viewer")
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        self.contentlayout = QtGui.QVBoxLayout(self)
        self.contentlayout.setContentsMargins(0,0,0,0)
        self.contentlayout.setSpacing(0)
        self.contentlayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setLayout(self.contentlayout)
        
        self.database = database.Database()
        
        self.banner_holder = BaseWidget(self,group=True,title="",
                                                        show=True)
        
        self.table_holder = BaseWidget(self,group=False,title="",
                                                        show=True)
        
        self.contentlayout.addWidget(self.banner_holder)
        self.contentlayout.addWidget(self.table_holder)
        
        self.table = DataBaseTable(self.database)
        self.table_holder.addWidget(self.table)
        
        self.connect(self.table, QtCore.SIGNAL('viewStructure(int)'), self.viewStructure)
        
        self.setup_search_buttons()
        
        self.database.init()
        
        self.banner_holder.show()
        self.table_holder.show()
        
        #self.table.populate({})
    
    def setup_search_buttons(self):
        
        
#         grid = self.banner_holder.newGrid()
#         self.database_entry = QtGui.QLineEdit(self.database.dbname)
#         self.database_entry.setMinimumWidth(200)
#         grid.addWidget(HolderWidget([QL("Database:"),self.database_entry]),0,0)
        
        
        nrows = 7
        wfactor=0.9
        
        self.user_holder = BaseWidget(self,group=True,title="User",show=True,align=QtCore.Qt.AlignTop)
        
        
        self.entries = {}
        grid = self.user_holder.newGrid()
        cols = {}
        labs = {}
        for i,field in enumerate(self.database.fields['users']):
            row,col = i % nrows, int(i/nrows)
            self.entries['users.'+field.tag] = QtGui.QLineEdit()
            self.entries['users.'+field.tag].setFixedWidth(60)
            l = QL(field.__repr__())
            try:
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col].append(l)
            except:
                cols[col] = []
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col] = []
                labs[col].append(l)
            
            #l.setFixedWidth(80)
            #labs.append(l)
            grid.addWidget(HolderWidget([l,self.entries['users.'+field.tag]]),row,col,1,1)
        
        
        for col in cols.keys():
            width = numpy.max(numpy.array(cols[col]))*wfactor
            for lab in labs[col]:lab.setFixedWidth(width)
                
        
        
        self.dual_lattice_holder = BaseWidget(self,group=True,title="Dual Lattice",
                                                            show=True,align=QtCore.Qt.AlignTop)
        
        cols = {}
        labs = {}
        
        grid = self.dual_lattice_holder.newGrid()
        for i,field in enumerate(self.database.fields['dual_lattices']):
            row,col = i % nrows, int(i/nrows)
            self.entries['dual_lattices.'+field.tag] = QtGui.QLineEdit()
            self.entries['dual_lattices.'+field.tag].setFixedWidth(60)
            l = QL(field.__repr__())
            try:
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col].append(l)
            except:
                cols[col] = []
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col] = []
                labs[col].append(l)
            grid.addWidget(HolderWidget([l,self.entries['dual_lattices.'+field.tag]]),row,col,1,1)
        
        for col in cols.keys():
            width = numpy.max(numpy.array(cols[col]))*wfactor
            for lab in labs[col]:lab.setFixedWidth(width)
        
        self.carbon_lattice_holder = BaseWidget(self,group=True,title="Carbon Lattice",
                                                            show=True,align=QtCore.Qt.AlignTop)
        
        cols = {}
        labs = {}
        grid = self.carbon_lattice_holder.newGrid()
        for i,field in enumerate(self.database.fields['carbon_lattices']):
            row,col = i % nrows, int(i/nrows)
            self.entries['carbon_lattices.'+field.tag] = QtGui.QLineEdit()
            self.entries['carbon_lattices.'+field.tag].setFixedWidth(60)
            l = QL(field.__repr__())
            try:
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col].append(l)
            except:
                cols[col] = []
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col] = []
                labs[col].append(l)
            grid.addWidget(HolderWidget([l,self.entries['carbon_lattices.'+field.tag]]),row,col,1,1)
        
        for col in cols.keys():
            width = numpy.max(numpy.array(cols[col]))*wfactor
            for lab in labs[col]:lab.setFixedWidth(width)
        
        self.rings_holder = BaseWidget(self,group=True,title="Rings",
                                                            show=True,align=QtCore.Qt.AlignTop)
        
        cols = {}
        labs = {}
        grid = self.rings_holder.newGrid()
        for i,field in enumerate(self.database.fields['rings']):
            row,col = i % nrows, int(i/nrows)
            self.entries['rings.'+field.tag] = QtGui.QLineEdit()
            self.entries['rings.'+field.tag].setFixedWidth(60)
            l = QL(field.__repr__())
            try:
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col].append(l)
            except:
                cols[col] = []
                cols[col].append(l.fontMetrics().boundingRect(l.text()).width())
                labs[col] = []
                labs[col].append(l)
            grid.addWidget(HolderWidget([l,self.entries['rings.'+field.tag]]),row,col,1,1)        
        
        for col in cols.keys():
            width = numpy.max(numpy.array(cols[col]))*wfactor
            for lab in labs[col]:lab.setFixedWidth(width)
        
        self.banner_holder.addWidgets([self.user_holder,self.dual_lattice_holder,self.carbon_lattice_holder,self.rings_holder])
        
        
        grid = self.banner_holder.newGrid()
        
        self.order_by_cb = QtGui.QComboBox()
        keys= numpy.sort(numpy.array(self.entries.keys()))
        for key in keys:
            self.order_by_cb.addItem(key)
        
        grid.addWidget(HolderWidget([QL("Sort by"),self.order_by_cb]),0,2,10,1)
        
        self.order_cb = QtGui.QComboBox()
        for key in ["Asc","Desc"]:
            self.order_cb.addItem(key)
        
        grid.addWidget(HolderWidget([QL("Order"),self.order_cb]),0,4,10,1)
        
        self.search_bt = QtGui.QPushButton("Search")
        self.connect(self.search_bt, QtCore.SIGNAL('clicked()'), self.new_search)
        #self.banner_holder.addWidget(self.search_bt)
        grid.addWidget(self.search_bt,0,10,10,1)
        
        
        self.clear_bt = QtGui.QPushButton("Clear")
        self.connect(self.clear_bt, QtCore.SIGNAL('clicked()'), self.clear_filters)
        #self.banner_holder.addWidget(self.search_bt)
        grid.addWidget(self.clear_bt,0,11,10,1)
        
        
    def clear_filters(self):
        for entry in self.entries.values():
            entry.clear()
        
    def new_search(self):
        self.database.init()
        self.table.clear()
        
        search_params = {}
        for key,entry in self.entries.items():
            
            val = str(entry.text()).strip()
            printl(key,val)
            if len(val) == 0: continue
            else: search_params[key] = val
            
        orderby = self.order_by_cb.currentText()
        order = self.order_cb.currentText()
        
        
        #self.database.set_database(self.database_entry.text())    
        self.table.populate(search_params,orderby,order)
        
    def viewStructure(self,row):
        #get structure from database row in self.table
        
        
#        
        uid,did,cid = self.table.user_ids[row],self.table.dual_lattice_ids[row],self.table.carbon_lattice_ids[row]
        structure  = self.database.construct_structure(did,cid)
        
        if(structure==None):
            #structure  = self.database.get_parent_structure(did)
            did,cid = self.database.get_parent_ids(did)
            printl("parent ids",did,cid)
            structure  = self.database.construct_structure(did,cid)
        
        if(structure==None):return
        printl("clicked",row,uid,did,cid)
        self.MainWindow.activateWindow()   
        self.MainWindow.gui.dock.toolbar.structurelist.addStructure(structure) 
            
    def bringToFront(self):
        self.raise_()
        self.show()
        
    def sizeHint(self):

        return QtCore.QSize(1200,500)       