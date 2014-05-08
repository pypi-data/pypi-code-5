import os
from tkMessageBox import showerror
from equations import *
from mkreport import MkReport


class AnalizeSpec(Equations,MkReport):

	MashNodeError = "Mashs or Nodes must be defined"

	def __init__(self):
		pass



	def analize(self):   # Collect & Evaluate file spec data
		# Get number of Mashs/Nodes if not defined
		if self.FileName != None:
			self.FileToUpper(self.FileName)
			execfile(self.UpFileName,self.GlobalDict,self.NetDict)
			self.RemoveUpperFile(self.UpFileName)
			try:
				if 'NODES' in self.NetDict:
					self.Nodes = self.NetDict['NODES']
					self.AnalType='Node'
				elif 'MASHS' in self.NetDict:
					self.Nodes = self.NetDict['MASHS']
					self.AnalType='Mash'
				else:
					raise MashNodeError

			except MashNodeError:
				showerror('Error','Mashs or Nodes must be defined')


		if self.Nodes < 2:
			showerror('Error', 'Enter Number of Mashs or Nodes.\nMust be 2 or higher.', 'Net Size', '2')



	def FileToUpper(self,file):
		self.UpFileName = self.BaseFileName + '.upper'
		lines = open(file,'r').readlines()
		out = open(self.UpFileName,'w')
		# Convert text to UpperCase unless the text is inside
		# a Comment
		for line in lines:
			psloc = line.find('#')
			if psloc == 0 :	# This whole line is a comment
				out.write(line)
			elif psloc > 0 :   # There a comment on this line
				newline = line[:psloc].upper() + line[psloc:]
				out.write(newline)
			else:			   # No comment on this line
				out.write(line.upper())
		out.close()

	def RemoveUpperFile(self,file):
		# Remove Upper Case File if defined
		if os.path.exists(file):
			os.remove(file)
			self.UpFileName=None
