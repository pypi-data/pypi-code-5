'''
Martin Bednar
martin.bednar@hotmail.sk
'''
from PyQt4 import QtCore, QtGui
import random as rn
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

a = 0
warning = "INPUT IS NOT ASCII"
warning_2 = "PARAPHRASE MUST BE AN INTEGER"
bool_ascii_in_stay = True
bool_crypt_spaces = True

class Caesar_Engine(object):

    def is_ascii(self,s):
        return all(ord(c) < 128 for c in s)

    def crypt_me(self,text,number):
        if(self.is_ascii(text)==False):
            return "INPUT IS NOT ASCII"
        else:
            len_text = len(text)
            len_number = len(str(number))
            output=''
            str_number = str(number)
            while(len(str_number)<=len_text):
                str_number=str_number+str_number
            for x in xrange(0,len_text):
                output = output + (chr(ord(text[x])+int(str_number[x])))
            return output
    def crypt_me_in_ASCII(self,text,number): #not good
        if(self.is_ascii(text)==False):
            return "INPUT IS NOT ASCII"
        else:
            len_text = len(text)
            len_number = len(str(number))
            output=''
            str_number = str(number)
            while(len(str_number)<=len_text):
                str_number=str_number+str_number
            for x in xrange(0,len_text):
                if((ord(text[x])>=65) and (ord(text[x])<=90)):
                    help = (ord(text[x])+int(str_number[x]))
                    if(help>90):
                        help = help - 26 
                        help = chr(help)       
                if((ord(text[x])>=97) and (ord(text[x])<=122)):
                    help = (ord(text[x])+int(str_number[x]))
                    if(help>122):
                        help = help - 26 
                        help = chr(help)
                if(not(((ord(text[x])>=65) and (ord(text[x])<=90)) or ((ord(text[x])>=97) and (ord(text[x])<=122)))):
                    help=text[x]
                if(type(help)==int):
                    help = chr(help)
                output = output + help
            return output

    def decrypt_me(self,text,number):
        len_text = len(text)
        len_number = len(str(number))
        output=''
        str_number = str(number)
        while(len(str_number)<=len_text):
            str_number=str_number+str_number
        for x in xrange(0,len_text):
            output = output + (chr(ord(text[x])-int(str_number[x])))
        return output

    def decrypt_me_in_ASCII(self,text,number):
        len_text = len(text)
        len_number = len(str(number))
        output=''
        str_number = str(number)
        while(len(str_number)<=len_text):
            str_number=str_number+str_number
        for x in xrange(0,len_text):
            if((ord(text[x])>=65) and (ord(text[x])<=90)):
                help = (ord(text[x])-int(str_number[x]))

                if(help<65):
                    help = help + 26 
                    help = chr(help)      
            if((ord(text[x])>=97) and (ord(text[x])<=122)):
                help = (ord(text[x])-int(str_number[x]))
                if(help<97):
                    help = help + 26 
                    help = chr(help)
            if(not(((ord(text[x])>=65) and (ord(text[x])<=90)) or ((ord(text[x])>=97) and (ord(text[x])<=122)))):
                help=text[x]
            if(type(help)==int):
                help = chr(help)
            output = output + help
        return output
    def random_paraphrase(self,a=1,b=1000000000000000000000000000):
        return rn.randint(a,b)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(554, 546)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 651, 551))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.Caesar = QtGui.QWidget()
        self.Caesar.setObjectName(_fromUtf8("Caesar"))
        self.pushButton = QtGui.QPushButton(self.Caesar)
        self.pushButton.setGeometry(QtCore.QRect(50, 210, 98, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self.Caesar)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 210, 98, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.textEdit = QtGui.QTextEdit(self.Caesar)
        global a 
        a = self.pushButton
        self.textEdit.setGeometry(QtCore.QRect(10, 30, 531, 111))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.lineEdit = QtGui.QLineEdit("123456",self.Caesar)
        self.lineEdit.setGeometry(QtCore.QRect(10, 170, 531, 27))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.textBrowser = QtGui.QTextBrowser(self.Caesar)
        self.textBrowser.setGeometry(QtCore.QRect(10, 270, 531, 131))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.label = QtGui.QLabel(self.Caesar)
        self.label.setGeometry(QtCore.QRect(10, 10, 181, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.Caesar)
        self.label_2.setGeometry(QtCore.QRect(10, 150, 91, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.Caesar)
        self.label_3.setGeometry(QtCore.QRect(20, 440, 66, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.Caesar)
        self.label_4.setGeometry(QtCore.QRect(480, 440, 66, 17))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.Caesar)
        self.label_5.setGeometry(QtCore.QRect(170, 440, 181, 17))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.pushButton_3 = QtGui.QPushButton(self.Caesar)
        self.pushButton_3.setGeometry(QtCore.QRect(180, 210, 171, 27))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.checkBox = QtGui.QCheckBox(self.Caesar)
        self.checkBox.setGeometry(QtCore.QRect(10, 410, 381, 22))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.tabWidget.addTab(self.Caesar, _fromUtf8(""))
        self.About = QtGui.QWidget()
        self.About.setObjectName(_fromUtf8("About"))
        self.label_6 = QtGui.QLabel(self.About)
        self.label_6.setGeometry(QtCore.QRect(30, 30, 61, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(self.About)
        self.label_7.setGeometry(QtCore.QRect(30, 60, 141, 17))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.About)
        self.label_8.setGeometry(QtCore.QRect(30, 90, 241, 17))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(self.About)
        self.label_9.setGeometry(QtCore.QRect(30, 120, 81, 17))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.line = QtGui.QFrame(self.About)
        self.line.setGeometry(QtCore.QRect(20, 160, 521, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_15 = QtGui.QLabel(self.About)
        self.label_15.setGeometry(QtCore.QRect(20, 190, 511, 31))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.label_16 = QtGui.QLabel(self.About)
        self.label_16.setGeometry(QtCore.QRect(20, 240, 371, 17))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.label_17 = QtGui.QLabel(self.About)
        self.label_17.setGeometry(QtCore.QRect(20, 280, 311, 17))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.line_2 = QtGui.QFrame(self.About)
        self.line_2.setGeometry(QtCore.QRect(20, 310, 521, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.tabWidget.addTab(self.About, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.label_14 = QtGui.QLabel(self.tab)
        self.label_14.setGeometry(QtCore.QRect(190, 210, 141, 20))
        self.label_14.setOpenExternalLinks(True)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.Author = QtGui.QWidget()
        self.Author.setObjectName(_fromUtf8("Author"))
        self.label_11 = QtGui.QLabel(self.Author)
        self.label_11.setGeometry(QtCore.QRect(30, 30, 101, 17))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_12 = QtGui.QLabel(self.Author)
        self.label_12.setGeometry(QtCore.QRect(30, 60, 201, 17))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.label_13 = QtGui.QLabel(self.Author)
        self.label_13.setGeometry(QtCore.QRect(30, 120, 361, 17))
        self.label_13.setOpenExternalLinks(True)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.label_18 = QtGui.QLabel(self.Author)
        self.label_18.setGeometry(QtCore.QRect(30, 150, 521, 21))
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.label_19 = QtGui.QLabel(self.Author)
        self.label_19.setGeometry(QtCore.QRect(30, 180, 531, 17))
        self.label_19.setOpenExternalLinks(True)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.label_10 = QtGui.QLabel(self.Author)
        self.label_10.setGeometry(QtCore.QRect(30, 90, 101, 17))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.tabWidget.addTab(self.Author, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 554, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionAuthor = QtGui.QAction(MainWindow)
        self.actionAuthor.setObjectName(_fromUtf8("actionAuthor"))
        self.actionLicense = QtGui.QAction(MainWindow)
        self.actionLicense.setObjectName(_fromUtf8("actionLicense"))

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.pressed.connect(self.set_output_text_crypt)
        self.pushButton_2.pressed.connect(self.set_output_text_decrypt)
        self.pushButton_3.pressed.connect(self.set_paraphrase)
        if(bool_ascii_in_stay==True):
            self.checkBox.toggle()
        self.checkBox.stateChanged.connect(self.box_changed_ascii)
        self.textBrowser.append("here will be output")
        self.pushButton.setCheckable(True)
        self.pushButton_2.setCheckable(True)
        self.pushButton_3.setCheckable(True)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "crypt_me", None))
        self.pushButton.setText(_translate("MainWindow", "crypt_me!", None))
        self.pushButton_2.setText(_translate("MainWindow", "decrypt_me!", None))
        self.label.setText(_translate("MainWindow", "Input Text (ASCII letters):", None))
        self.label_2.setText(_translate("MainWindow", "Paraphrase:", None))
        self.label_3.setText(_translate("MainWindow", "bo_92", None))
        self.label_4.setText(_translate("MainWindow", "2014", None))
        self.label_5.setText(_translate("MainWindow", "martin.bednar@hotmail.sk", None))
        self.pushButton_3.setText(_translate("MainWindow", "Generate Paraphrase", None))
        self.checkBox.setText(_translate("MainWindow", "Stay in ASCII letters only a-z and A-Z will be crypted", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Caesar), _translate("MainWindow", "Caesar", None))
        self.label_6.setText(_translate("MainWindow", "crypt_me", None))
        self.label_7.setText(_translate("MainWindow", "version 0.12", None))
        self.label_8.setText(_translate("MainWindow", "programming language: python 2.7", None))
        self.label_9.setText(_translate("MainWindow", "GUI: PyQt4", None))
        self.label_15.setText(_translate("MainWindow", "Generate Paraphrase - generate random paraphrase (random int number)", None))
        self.label_16.setText(_translate("MainWindow", "crypt_me! - will crypt input text", None))
        self.label_17.setText(_translate("MainWindow", "decrypt_me! - will decrypt input text", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.About), _translate("MainWindow", "About", None))
        self.label_14.setText(_translate("MainWindow", "<a href=\"http://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3\">GNU GPL v3 license</a>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "License", None))
        self.label_11.setText(_translate("MainWindow", "Martin Bednar", None))
        self.label_12.setText(_translate("MainWindow", "martin.bednar@hotmail.sk", None))
        self.label_13.setText(_translate("MainWindow", "<a href=\"https://pypi.python.org/pypi/crypt_me\">https://pypi.python.org/pypi/crypt_me</a>", None))
        self.label_18.setText(_translate("MainWindow", "youtube channel: ", None))
        self.label_19.setText(_translate("MainWindow", "<a href=\"https://www.youtube.com/channel/UCIjDDB2ArihwUd4664SQD1Aabelbel\"><a href=\"https://pypi.python.org/pypi/crypt_me\">https://www.youtube.com/channel/UCIjDDB2ArihwUd4664SQD1Aabelbel</a></a>", None))
        self.label_10.setText(_translate("MainWindow", "Source code:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Author), _translate("MainWindow", "Author", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionAuthor.setText(_translate("MainWindow", "Author", None))
        self.actionLicense.setText(_translate("MainWindow", "License", None))

    def set_output_text_crypt(self, pressed = True):
        if(pressed):
            global a
            a=self.textEdit
            try:
                text = str(self.textEdit.toPlainText())
                lineEdit = str(self.lineEdit.text())
                global bool_ascii_in_stay
                if(bool_ascii_in_stay==False):
                    crypt = caesar.crypt_me(text,lineEdit)
                else:
                    crypt = caesar.crypt_me_in_ASCII(text,lineEdit)
                self.textBrowser.clear()
                self.textBrowser.append(crypt)
            except UnicodeEncodeError:
                self.textBrowser.clear()
                global warning
                self.textBrowser.append(warning)
            except ValueError:
                self.textBrowser.clear()
                global warning_2
                self.textBrowser.append(warning_2)

    def set_output_text_decrypt(self, pressed = True):
        if(pressed):
            text = str(self.textEdit.toPlainText())
            lineEdit = str(self.lineEdit.text())
            global bool_ascii_in_stay
            if(bool_ascii_in_stay==False):
                decrypt = caesar.decrypt_me(text,lineEdit)
            else:
                decrypt = caesar.decrypt_me_in_ASCII(text,lineEdit)
            self.textBrowser.clear()
            self.textBrowser.append(decrypt)

    def box_changed_ascii(self,state):
        global bool_ascii_in_stay
        if(bool_ascii_in_stay == True):
            bool_ascii_in_stay = False
        else:
            bool_ascii_in_stay = True

    def set_paraphrase(self,pressed = True):
        if(pressed):
            para = caesar.random_paraphrase()
            self.lineEdit.clear()
            self.lineEdit.insert(str(para))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    caesar = Caesar_Engine()
    sys.exit(app.exec_())

