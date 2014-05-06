# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# advas i/o module
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

class AdvasIo:
	def __init__(self, filename, encoding):
		"init an Advas I/O object"

		self.setFilename(filename)
		self.setEncoding(encoding)
		self.contents = ""
		self.error = False

		return

	def getFilename(self):
		return self.filename

	def setFilename(self, filename):
		self.filename = filename
		return

	def getEncoding(self):
		return self.encoding

	def setEncoding(self, encoding):
		self.encoding = encoding
		return

	def getError(self):
		return self.error

	def readFileContents(self):
		"read the given file"
		try:
			fileId = open(self.filename, "r")
			self.contents = fileId.readlines()
			fileId.close()
		except:
			self.error = True
			return False
		return True

	def getFileContents(self):
		"returns the content of the opened file"
		return self.contents

