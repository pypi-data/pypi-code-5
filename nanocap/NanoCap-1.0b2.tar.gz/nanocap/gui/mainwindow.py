'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

GUI mainwindow

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
from nanocap.gui.settings import *
from nanocap.gui import gui
from nanocap.core import globals

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setMinimumWidth(1100)
        self.setMinimumHeight(750)
        self.setStyleSheet(STYLESHEET)
        self.show()
    
    def setGUI(self,gui):
        self.gui = gui
        
    def closeEvent(self, event):  
        if(globals.DEBUG):
            self.gui.threadManager.stop()
            QtGui.QApplication.quit()  
                   
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to exit NanoCap?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            self.gui.threadManager.stop()
            QtGui.QApplication.quit()

        else:
            event.ignore()
            
        return
