#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Martin Bednar
'''
import sys
from PyQt4 import QtGui, QtCore
a = 0
warning = "INPUT IS NOT ASCII"
warning_2 = "PARAPHRASE MUST BE AN INTEGER"
bool_ascii_in_stay = True
bool_crypt_spaces = True

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def crypt_me(text,number):
    if(is_ascii(text)==False):
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
def crypt_me_in_ASCII(text,number): #not good
    if(is_ascii(text)==False):
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

def decrypt_me(text,number):
    len_text = len(text)
    len_number = len(str(number))
    output=''
    str_number = str(number)
    while(len(str_number)<=len_text):
        str_number=str_number+str_number
    for x in xrange(0,len_text):
        output = output + (chr(ord(text[x])-int(str_number[x])))
    return output

def decrypt_me_in_ASCII(text,number):
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

class GUI_Crypt_me(QtGui.QWidget):
    
    
    def __init__(self):
        super(GUI_Crypt_me, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        
        self.text_in = QtGui.QTextEdit(self)
        self.text_out = QtGui.QTextBrowser(self)

        crypt_button = QtGui.QPushButton("Crypt_me!",self)
        crypt_button.setCheckable(True)
        crypt_button.move(100, 210)

        decrypt_button = QtGui.QPushButton("Decrypt_me!",self)
        decrypt_button.setCheckable(True)

        self.paraphrase = QtGui.QLineEdit("123",self)

        label_0 = QtGui.QLabel("Caesar cipher",self)
        label_1 = QtGui.QLabel("Input text (ASCII letters):",self)
        label_2 = QtGui.QLabel("Paraphrase: (must be an integer number)",self)
        label_3 = QtGui.QLabel("Output text:",self)
        label_4 = QtGui.QLabel("bo_92 2014          martin.bednar@hotmail.sk",self)
        stay_in_ascii = QtGui.QCheckBox('Output Stay in ASCII Letters (only letters a-z, A-Z are Crypted)', self)
        #crypt_spaces = QtGui.QCheckBox('Crypt spaces', self)
        if(bool_ascii_in_stay==True):
            stay_in_ascii.toggle()
        '''if(bool_crypt_spaces==True):
            crypt_spaces.toggle()'''
        stay_in_ascii.stateChanged.connect(self.box_changed_ascii)
        #crypt_spaces.stateChanged.connect(self.box_changed_spaces)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(label_0)
        vbox.addWidget(label_1)
        vbox.addWidget(self.text_in)
        vbox.addWidget(label_2)
        vbox.addWidget(self.paraphrase)
        vbox.addWidget(crypt_button)
        vbox.addWidget(decrypt_button)
        vbox.addWidget(label_3)
        self.text_out.append("here will be output")
        vbox.addWidget(self.text_out)
        vbox.addWidget(stay_in_ascii)
        #vbox.addWidget(crypt_spaces)
        vbox.addWidget(label_4)

        crypt_button.clicked[bool].connect(self.set_output_text_crypt)
        decrypt_button.clicked[bool].connect(self.set_output_text_decrypt)
        self.setLayout(vbox)
        self.setGeometry(300, 300, 500, 150)
        self.setWindowTitle('Crypt_me!')
        self.show()


    def set_output_text_crypt(self, pressed):
        source = self.sender()
        if(pressed):
            global a
            a=self.text_in
            try:
                text = str(self.text_in.toPlainText())
                paraphrase = str(self.paraphrase.text())
                global bool_ascii_in_stay
                if(bool_ascii_in_stay==False):
                    crypt = crypt_me(text,paraphrase)
                else:
                    crypt = crypt_me_in_ASCII(text,paraphrase)
                self.text_out.clear()
                self.text_out.append(crypt)
            except UnicodeEncodeError:
                self.text_out.clear()
                global warning
                self.text_out.append(warning)
            except ValueError:
                self.text_out.clear()
                global warning_2
                self.text_out.append(warning_2)

    def set_output_text_decrypt(self, pressed):
        source = self.sender()
        if(pressed):
            text = str(self.text_in.toPlainText())
            paraphrase = str(self.paraphrase.text())
            global bool_ascii_in_stay
            if(bool_ascii_in_stay==False):
                decrypt = decrypt_me(text,paraphrase)
            else:
                decrypt = decrypt_me_in_ASCII(text,paraphrase)
            self.text_out.clear()
            self.text_out.append(decrypt)

    def box_changed_ascii(self,state):
        global bool_ascii_in_stay
        if(bool_ascii_in_stay == True):
            bool_ascii_in_stay = False
        else:
            bool_ascii_in_stay = True

    '''def box_changed_spaces(self,state):
        global bool_crypt_spaces
        if(bool_crypt_spaces == True):
            bool_crypt_spaces = False
        else:
            bool_crypt_spaces = True'''
           

        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = GUI_Crypt_me()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()