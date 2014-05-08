
import os
from Tkinter import *
from tkMessageBox import showerror

class DisReport:
	def __init__(self,parent,filename,lable=None):
		self.parent=parent
		self.top = parent
		self.fn = filename
		self.top = Toplevel(parent)
		fn = os.path.basename(self.fn)
		self.top.title(fn)
		self.top.geometry('+150+250')
		self.top.grab_set()

		self.top.protocol("WM_DELETE_WINDOW", self.close_dia)
		self.initial_focus = self.show()
		self.parent.wait_window(self.top)


	def show(self):
		if os.path.exists(self.fn):
			tw = Text(self.top)
			scroll =Scrollbar(self.top, command=tw.yview)
			button = Button(self.top, text='Quit',command=self.close_dia)
			tw.config(yscrollcommand=scroll.set)
			tw.config(borderwidth=3)
			tw.config(state=NORMAL)
			tw.delete(1.0,END)
			fin = open(self.fn, 'r')
			while(True):
				line = fin.readline()
				if not line: break
				tw.insert(END,line)
			tw.config(state=DISABLED)
			scroll.pack(side=RIGHT, fill=Y)
			tw.pack(expand=1,fill=BOTH)
			button.pack()
		else:
			errmes = 'File ' + self.fn + ' can not be found!'
			showerror('FileOpenError', errmes)


	def close_dia(self, event=None):
		self.top.withdraw()
		self.top.update_idletasks()
		self.parent.focus_set()
		self.top.destroy()




if __name__ == "__main__":

	from Tkinter import *
	root = Tk()
#	root.title("Test Display")

	fn = "/home/jim/test/Wein_Bridge.report"
	dp = DisReport(root,fn)



