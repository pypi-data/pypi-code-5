# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# advas core module
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

# other modules required by advas
import string
import re
import math
from ngram import Ngram
from phonetics import Phonetics
from advasio import AdvasIo

class Advas:
	def __init__(self, text, encoding):
		"init an Advas object"

		self.setText(text)
		self.setEncoding(encoding)

		return

	def getText(self):
		"return the saved text value"
		return self.text

	def setText(self, text):
		"set a given text value"
		self.text = text
		return

	def getEncoding(self):
		"return the saved text encoding"
		return self.encoding

	def setEncoding(self, encoding):
		"set the text encoding"
		self.encoding = encoding
		return

	# basic functions ==========================================
	# line -----------------------------------------------------

	def splitLine (self, line):
		"split a line of text into single words"

		# define regexp tokens and split line
		tokens = re.compile(r"[\w']+")
		return tokens.findall(line)

	def splitParagraph (self):
		"split a paragraph into single lines"
		lines = self.text
		return lines

	def splitText(self):
		"split the text into single words per paragraph line"

		paragraphList = []

		# split text into single lines
		lines = self.splitParagraph()
		for line in lines:
			# split this line into single words
			wordList = self.splitLine(line)
			paragraphList.append(wordList)

		return paragraphList

	def isComment(self, line):
		"verifies a line for being a UNIX style comment"
		
		# remove any whitespace at the beginning
		line = string.lstrip(line)

		# is comment? (UNIX style)
		if line.startswith("#"):
			return True
		else:
			return False

	def kmpSearch(self, text, pattern):
		"search pattern in a text using Knuth-Morris-Pratt algorithm"
		
		i = 0
		j = -1
		next = {0: -1}

		# initialize next array
		while 1:
			if ((j == -1) or (pattern[i] == pattern[j])):
				i = i + 1
				j = j + 1
				next[i] = j
			else:
				j = next[j]
			# end if

			if (i >= len(pattern)):
				break
		# end while

		# search
		i = 0
		j = 0
		positions = []

		while 1:
			if ((j == -1) or (text[i] == pattern[j])):
				i = i + 1
				j = j + 1
			else:
				j = next[j]
			# end if

			if (i >= len(text)):
				return positions
			# end if

			if (j >= len(pattern)):
				positions.append(i - len(pattern))
				i = i - len(pattern) + 1
				j = 0
			# end if
		# end while
		return

	# list functions -------------------------------------------

	def removeItems(self, originalList, removeList):
		"remove the items from the original list"

		for item in removeList:
			# item in original list?
			if originalList.has_key(item):
				del originalList[item]

		return originalList

	# advanced functions =======================================
	# term frequency (tf) --------------------------------------

	def tf (self):
		"calculates the term frequency for the given text"

		occurency = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if occurency.has_key(word):
					newValue = occurency[word] + 1
				else:
					newValue = 1
				occurency[word] = newValue
					
		# return list of words and their frequency
		return occurency

	def tfStop (self, stopList):
		"calculates the term frequency and removes the items given in stop list"

		# get term frequency from self.text
		wordList = self.tf()

		# remove items given in stop list
		ocurrency = self.removeItems(wordList, stopList)

		# return result
		return ocurrency
		
	def idf(self, numberOfDocuments, frequencyList):
		"calculates the inverse document frequency for a given list of terms"
		
		idfList = {}
		for item in frequencyList.keys():
			# get frequency
			frequency = frequencyList[item]

			# calculate idf = ln(numberOfDocuments/n):
			# n=number of documents that contain term
			idf = math.log(float(numberOfDocuments)/float(frequency))

			# save idf
			idfList[item] = idf
			
		return idfList

	# n-gram functions ----------------------------------------

	def getNgramsByWord (self, word, ngramSize):
		if not ngramSize:
			return []

		term = Ngram(word, ngramSize)
		if term.deriveNgrams():
			return term.getNgrams()
		else:
			return []

	def getNgramsByLine (self, ngramSize):
		if not ngramSize:
			return []

		occurency = []

		# split the given text into single lines
		lines = self.splitParagraph()
		for line in lines:
			term = Ngram(line, ngramSize)
			if term.deriveNgrams():
				occurency.append(term.getNgrams())
			else:
				occurency.append([])
		return occurency

	def getNgramsByParagraph(self, ngramSize):
		if not ngramSize:
			return []

		reducedList = []
		occurency = self.getNgramsByLine(ngramSize)
		for line in occurency:
			reducedList = list(set(reducedList) | set(line))
		return reducedList

	def compareNgramLists (self, list1, list2):
		"compares two lists of ngrams and returns their degree of equality"
		# equality of terms : Dice coefficient
		# 
		# S = 2C/(A+B)
		#
		# S = degree of equality
		# C = n-grams contained in term 2 as well as in term 2
		# A = number of n-grams contained in term 1
		# B = number of n-grams contained in term 2

		# find n-grams contained in both lists
		A = len(list1)
		B = len(list2)

		# extract the items which appear in both list1 and list2
		list3 = list(set(list1) & set(list2))
		C = len(list3)

		# calculate similarity of term 1 and 2
		S = float(float(2*C)/float(A+B))

		return S

	# phonetic codes ---------------------------------------

	def soundex(self):
		soundexCode = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if not soundexCode.has_key(word):
					phoneticsObject = Phonetics(word)
					soundexValue = phoneticsObject.soundex()
					soundexCode[word] = soundexValue

		return soundexCode

	def metaphone(self):
		metaphoneCode = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if not metaphoneCode.has_key(word):
					phoneticsObject = Phonetics(word)
					metaphoneValue = phoneticsObject.metaphone()
					metaphoneCode[word] = metaphoneValue

		return metaphoneCode

	def nysiis(self):
		nysiisCode = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if not nysiisCode.has_key(word):
					phoneticsObject = Phonetics(word)
					nysiisValue = phoneticsObject.nysiis()
					nysiisCode[word] = nysiisValue

		return nysiisCode

	def caverphone(self):
		caverphoneCode = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if not caverphoneCode.has_key(word):
					phoneticsObject = Phonetics(word)
					caverphoneValue = phoneticsObject.caverphone()
					caverphoneCode[word] = caverphoneValue

		return caverphoneCode

	def phoneticCode(self):
		codeList = {}

		# split the given text into single lines
		splittedParagraph = self.splitText()
		for line in splittedParagraph:
			for word in line:
				if not codeList.has_key(word):
					phoneticsObject = Phonetics(word)
					value = phoneticsObject.phoneticCode()
					codeList[word] = value

		return codeList

	# language detection -----------------------------------
	
	def isLanguage (self, keywordList):
		"given text is written in a certain language"

		# old function - substituted by isLanguageByKeywords()
		return self.isLanguageByKeywords (keywordList)

	def isLanguageByKeywords (self, keywordList):
		"determine the language of a given text with the use of keywords"

		# keywordList: list of items used to determine the language
		
		# get term frequency using tf
		textTf = self.tf()
		
		# lower each keyword
		listLength = len(keywordList)
		for i in range(listLength):
			keywordList[i] = string.lower(string.strip(keywordList[i]))
		# end for

		# derive intersection
		intersection = list(set(keywordList) & set(textTf.keys()))
		lineLanguage = len(intersection)

		# value
		value = float(float(lineLanguage)/float(listLength))

		return value

	# synonyms ---------------------------------------------
	
	def getSynonyms(self, filename, encoding):
		
		# works with OpenThesaurus (plain text version)
		# requires an OpenThesaurus release later than 2003-10-23
		# http://www.openthesaurus.de
		
		synonymFile = AdvasIo(filename, encoding)
		success = synonymFile.readFileContents()
		if not success:
			return False
		
		contents = synonymFile.getFileContents()
		searchTerm = self.text[0]
		synonymList = []
		
		for line in contents:
			if not self.isComment(line):
				wordList = line.split(";")
				if searchTerm in wordList:
					synonymList += wordList
		
		# remove extra characters
		for i in range(len(synonymList)):
			synonym = synonymList[i]
			synonymList[i] = synonym.strip()
		
		# compact list: remove double entries
		synonymList = 	list(set(synonymList))
		
		# maybe the search term is in the list: remove it, too
		if searchTerm in synonymList:
			synonymList = list(set(synonymList).difference(set([searchTerm])))
		
		return synonymList
		
	def isSynonymOf(self, term, filename, encoding):
		synonymList = self.getSynonyms(filename, encoding)
		if term in synonymList:
			return True
 
		return False

