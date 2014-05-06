# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# advas core module
#
# (C) 2002 - 2012 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

# other modules required by advas
import string
import re
import math

class Advas:
	def __init__(self):
		"init an Advas object"

		self.initFilename()
		self.initLine()
		self.initWords()
		self.initList()
		#self.init_ngrams()

		return

	def reInit (self):
		"re-initializes an Advas object"
		self.__init__()
		return

	# basic functions ==========================================
	# file name ------------------------------------------------

	def initFilename (self):
		self.filename = ""
		self.useFilename = False
		
	def setFilename (self, filename):
		self.filename = filename

	def getFilename (self):
		return self.filename

	def setUseFilename (self):
		self.useFilename = True

	def getUseFilename (self):
		return self.useFilename

	def setUseWordlist (self):
		self.useFilename = False

	def getFileContents (self, filename):
		try:
			fileId = open(fileame, "r")
		except:
			print "[AdvaS] I/O Error - can't open given file:", filename
			return -1

		# get file contents
		contents = fileId.readlines()

		# close file
		fileId.close()

		return contents
	
	# line -----------------------------------------------------

	def initLine (self):
		self.line = ""
	
	def setLine (self, line):
		self.line = line

	def getLine (self):
		return self.line

	def splitLine (self):
		"split a line of text into single words"

		# define regexp tokens and split line
		tokens = re.compile(r"[\w']+")
		self.words = tokens.findall(self.line)

	# words ----------------------------------------------------

	def initWords (self):
		self.words = {}

	def setWords (self, words):
		self.words = words
		
	def getWords (self):
		return self.words

	def countWords(self):
		"count words given in self.words, return pairs word:frequency"

		list = {}	# start with an empty list

		for item in self.words:
			# assume a new item
			frequency = 0
			
			# word already in list?
			if list.has_key(item):
				frequency = list[item]
			frequency += 1

			# save frequency , update list
			list[item] = frequency

		# save list of words
		self.set_list (list)

	# lists ----------------------------------------------------

	def initList (self):
		self.list = {}

	def setList (self, list):
		self.list = list

	def getList (self):
		return self.list

	def mergeLists(self, *lists):
		"merge lists of words"

		newList = {} 	# start with an empty list

		for currentList in lists:
			key = currentList.keys()
			for item in key:
				# assume a new item
				frequency = 0
				
				# item already in newlist?
				if newlist.has_key(item):
					frequency = newList[item]

				frequency += currentList[item]
				newList[item] = frequency
		# set list
		self.setList (newList)

	#def mergeListsIdf(self, *lists):
	#	"merge lists of words for calculating idf"
	#
	#	newlist = {}
	#
	#	for current_list in lists:
	#		key = current_list.keys()
	#		for item in key:
	#			# assume a new item
	#			frequency = 0
	#			
	#			# item already in newlist?
	#			if newlist.has_key(item):
	#				frequency = newlist[item]
	#			frequency += 1
	#			newlist[item] = frequency
	#	# set list
	#	self.set_list (newlist)
	#
	#def compact_list(self):
	#	"merges items appearing more than once"
	#
	#	newlist = {}
	#	original = self.list
	#	key = original.keys()
	#
	#	for j in key:
	#		item = string.lower(string.strip(j))
	#
	#		# assume a new item
	#		frequency = 0
	#
	#		# item already in newlist?
	#		if newlist.has_key(item):
	#			frequency = newlist[item]
	#		frequency += original[j]
	#		newlist[item] = frequency
	#
	#	# set new list
	#	self.set_list (newlist)
	#
	#def remove_items(self, remove):
	#	"remove the items from the original list"
	#
	#	newlist = self.list
	#
	#	# get number of items to be removed
	#	key = remove.keys()
	#
	#	for item in key:
	#		# item in original list?
	#		if newlist.has_key(item):
	#			del newlist[item]
	#
	#	# set newlist
	#	self.set_list(newlist)


