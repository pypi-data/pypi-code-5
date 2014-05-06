# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# entry module
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

from advas import Advas

class Entry:
	def __init__(self, text, encoding, keywords, classification):
		self.entryId = 0
		self.data = Advas(text, encoding)
		self.keywords = keywords
		self.classification = classification
		return

	def getEntryId(self):
		return self.entryId

	def setEntryId(self, value):
		self.entryId = value
		return

	def getText(self):
		return self.data.getText()

	def getEncoding(self):
		return self.data.getEncoding()

	def setEncoding(selv, encoding):
		self.data.setEncoding(encoding)
		return

	def getKeywords(self):
		return self.keywords

	def setKeywords(self, keywords):
		self.keywords = keywords
		return

	def getClassification(self):
		return self.classification

	def setClassification(self, classification):
		self.classification = classification
		return

	def getEntry(self):
		entry = {
			"entryId": self.getEntryId(),
			"text": self.getText(),
			"encoding": self.getEncoding(),
			"keywords": self.getKeywords(),
			"classification": self.getClassification()
		}
		return entry

	def getPhoneticCode(self):
		return self.data.phoneticCode()
