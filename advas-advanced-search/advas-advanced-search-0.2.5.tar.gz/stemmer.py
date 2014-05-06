# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# module containing stemming algorithms
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

from advasio import AdvasIo
import string
from phonetics import Phonetics
from ngram import Ngram
from advas import Advas

class Stemmer:

	def __init__(self, encoding):
		self.stemFile = ""
		self.encoding = encoding
		self.stemTable = {}
		return

	def loadStemFile(self, stemFile):
		if stemFile:
			self.stemFile = stemFile
			fileId = AdvasIo(self.stemFile, self.encoding)
			success = fileId.readFileContents()
			if not success:
				self.stemFile = ""
				return False
			else:
				contents = fileId.getFileContents()
				for line in contents:
					left, right = line.split(":")
					self.stemTable[string.strip(left)] = string.strip(right)
				return True
		else:
			self.stemFile = ""
			return False

	def clearStemFile(self):
		self.stemTable = {}
		self.stemFile = ""
		return
		
	def tableLookup(self, term):
		if term in self.stemTable:
			return self.stemTable[term]
		return

	def successorVariety (self, term, wordList):
		"calculates the terms'stem according to the successor variety algorithm"

		# get basic list for the variety	
		varObject = Phonetics("")
		sv = varObject.calcSuccVarietyList(wordList)
		svm = varObject.calcSuccVarietyMerge(sv)
		svmList = varObject.calcSuccVarietyCount(svm)

		# examine given term
		# use peak-and-plateau method to found word boundaries
		termLength = len(term)
		termRange = range(1, termLength-1)

		# start here
		start=0

		# list of stems
		stemList = []

		for i in termRange:
			# get slice
			wordSlice = term[start:i+1]
			# print word_slice

			# check for a peak
			A = term[i-1]
			B = term[i]
			C = term[i+1]
			
			a = 0
			if svmList.has_key(A):
				a = svmList[A]
				
			b = 0
			if svmList.has_key(B):
				b = svmList[B]

			c = 0
			if svmList.has_key(C):
				c = svmList[C]
				
			if (b>a) and (b>c):
				# save slice as a stem
				stemList.append(wordSlice)

				# adjust start
				start=i+1
			# end if
		# end for

		if (i<termLength):
			# still something left in buffer?
			wordSlice = term[start:]
			stemList.append(wordSlice)
		# end if

		# return result
		return stemList

	def ngramStemmer (self, wordList, size, equality):
		"reduces wordList according to the n-gram stemming method"
		
		# use return_list and stop_list for the terms to be removed, later
		returnList = []
		stopList = []
		ngramAdvas = Advas("","")

		# calculate length and range
		listLength = len(wordList)
		outerListRange = range(0, listLength)
		
		for i in outerListRange:
			term1 = wordList[i]
			innerListRange = range (0, i)
			
			# define basic n-gram object
			term1Ngram = Ngram(term1, 2)
			term1Ngram.deriveNgrams()
			term1NgramList = term1Ngram.getNgrams()

			for j in innerListRange:
				term2 = wordList[j]
				term2Ngram = Ngram(term2, 2)
				term2Ngram.deriveNgrams()
				term2NgramList = term2Ngram.getNgrams()
				
				# calculate n-gram value
				ngramSimilarity = ngramAdvas.compareNgramLists (term1NgramList, term2NgramList)
	
				# compare
				degree = ngramSimilarity - equality
				if (degree>0):
					# ... these terms are so similar that they can be conflated
					# remove the longer term, keep the shorter one
					if (len(term2)>len(term1)):
						stopList.append(term2)
					else:
						stopList.append(term1)
					# end if
				# end if
			# end for
		# end for

		# conflate the matrix
		# remove all the items which appear in stopList
		return list(set(wordList) - set(stopList))
		 