from Tkinter import *

import tkFileDialog
import webbrowser,os

from analize import AnalizeSpec
from equations import Equations
from mkreport import MkReport
from plotutil import matplot


class NetAna(AnalizeSpec):
	def __init__(self, master):
		self.opt = options = {}
		options['defaultextension']='.txt'
		options['filetypes']=[('text files', '.txt')]
		options['parent']=master
		options['title']='Get File Name'

		self.bld_menu(master)
		self.bld_widgets(master)
		self.parent=master

	def bld_menu(self, master):
		mBar = Menu(master, relief='groove', borderwidth=5)
		filemenu = Menu(mBar, tearoff=0)
		filemenu.add_command(label='SpecFile', underline=0,
			command = self.getspecfn)
		filemenu.add_separator()
		filemenu.add_command(label='Exit',
			underline=0, command=master.destroy)
		mBar.add_cascade(label='File', menu=filemenu)
		helpmenu = Menu(mBar, tearoff=0)
		helpmenu.add_command(label='Doc', underline=0, command=self.helpdoc)
		helpmenu.add_command(label='About', underline=0, command=self.about)
		mBar.add_cascade(label='Help', menu=helpmenu)
		master.config(menu=mBar)

	def bld_widgets(self, master):
		fm = Frame(master)
		Label(fm, text="Network Analizer", fg='red', font=('20')
		    ).pack(side=TOP, pady=10)
		fm.pack()
		fm1 = Frame(master)
		bt1=Button(fm1,text='Enter Spec. File Name', command=self.getspecfn
			).grid(row=0, sticky=E+W,padx=5,pady=5)
		bt2=Button(fm1,text='Enter Network Equations', command=self.getequ
			).grid(row=0, column=1, sticky=E+W,padx=5,pady=5)

		bt3=Button(fm1,text='Analize Network',command=self.mkreport
			).grid(row=1, sticky=E+W,padx=5,pady=5)
		b4=Button(fm1,text='Plot Network Results',command=self.plot
			).grid(row=1, column=1, sticky=E+W,padx=5,pady=5)

		Button(fm1, text='Quit', command=master.destroy
			).grid(row=2, sticky=W,padx=5,pady=5)
		fm1.pack(anchor=W)
		master.bind_all('<F1>',self.helpdoc)


	def getspecfn(self):
		file=tkFileDialog.askopenfilename(**self.opt)
		self.FileName=file
		self.BaseFileName=file[:-4]
		self.EquFileName = self.BaseFileName + '.equ'
		self.UpFileName= self.BaseFileName + '.upper'
		self.ReportFile= self.BaseFileName + '.report'
		self.NetFileName = self.BaseFileName + '.net'
		self.Nodes=0
		self.AcDc=''
		self.AnalType=''
		self.FreqUnits=''
		self.Mat=[]
		self.GlobalDict={"__builtins__":None}  # This makes using exec and eval much safer to use
		self.NetDict={}
		self.XCompDict={}

	def getequ(self):
		AnalizeSpec.analize(self)
		Equations.getequ(self)


	def mkreport(self):
		MkReport.mkreport(self)


	def plot(self):
		if  self.AcDc == "AC" :   # Plot AC Response
			matplot(fn=self.ReportFile, units=self.FreqUnits,ylab='None')
		else:  # Plot DC Response
			if self.AnalType == 'Node':
				ylabel = 'Volts'
			else:
				ylabel = 'Amps'
			matplot(fn=self.ReportFile, units='',ylab=ylabel)

	def helpdoc(self,event=None):
		prog_dir = os.path.dirname(sys.argv[0])
		doc = os.path.join(prog_dir, "doc/NetAnaDoc.html")
		webbrowser.open(doc,new=2)

	def about(self,event=None):
		prog_dir = os.path.dirname(sys.argv[0])
		doc = os.path.join(prog_dir, "doc/about.html")
		webbrowser.open(doc,new=2)

def main():
	root = Tk()
	root.title('NetAna')
	root.geometry('+100+200')
	app = NetAna(root)
	root.mainloop()


if __name__ == "__main__" :
	main()
