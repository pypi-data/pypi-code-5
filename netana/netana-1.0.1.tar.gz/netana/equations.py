
from griddialog import *
from wequ import wequ
import cPickle
from tkMessageBox import showerror

class Equations:
	def __init__(self,parent):
		self.parent = parent

	def getequ(self):
		# Build Grid Table and get Equations
		if os.path.exists(self.EquFileName):
			self.RestoreEquations()
			dig = GridDialog(self.parent,self.Mat,collab=self.AnalType)
			self.cleanup(dig)
		elif os.path.exists(self.NetFileName):
			self.Mat = wequ(self.NetFileName)
			dig = GridDialog(self.parent,self.Mat,collab=self.AnalType)
			self.cleanup(dig)
		else:
			dig = GridDialog(self.parent,size=self.Nodes,collab=self.AnalType)
			self.cleanup(dig)


	def cleanup(self,dig):
		if dig.status == "Save":
			self.Mat = dig.get()
			self.SaveEquations()
		if dig.top:	dig.top.destroy()

	def SaveEquations(self):
		# Save Mat Equations to file
		if len(self.Mat) > 1:	# if it has been defined
			cPickle.dump(self.Mat, open(self.EquFileName ,'wb'))

	def RestoreEquations(self):
		if os.path.exists(self.EquFileName):
			self.Mat=cPickle.load(open(self.EquFileName,'rb'))



if __name__ == "__main__":

	import os,cPickle
	from Tkinter import *

	root = Tk()

	os.chdir('/home/jim/test')


	eq = Equations(root)
	eq.Mat = [[1,2,3,4],
			[5,6,7,8],
			[9,10,11,12],
			[13,14,15,16]]

	eq.AnalType = "Node"
	eq.Nodes=4
	#eq.EquFileName = "/home/jim/test/Wein_Bridge.equb"
	eq.NetFileName = "/home/jim/test/BainterFilter.net"
	eq.EquFileName=""
	#eq.NetFileName=""
	eq.getequ()

	print 'Mat = ', eq.Mat

	root.mainloop()
