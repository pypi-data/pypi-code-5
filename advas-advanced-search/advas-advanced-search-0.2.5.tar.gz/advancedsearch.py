# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# search engine module
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

import math

class AdvancedSearch:
	def __init__(self):
		"initializes a new AdvancedSearch object"
		self.entryList = []
		self.stopList = []
		self.setSortOrderDescending()
		self.setSearchStrategy(50, 50)
		return

	# sort order

	def setSortOrderAscending(self):
		"changes sort order to ascending"
		self.sortOrderDescending = False
		return

	def setSortOrderDescending(self):
		"changes sort order to descending"
		self.sortOrderDescending = True
		return

	def reverseSortOrder(self):
		"reverses the current sort order"
		if self.getSortOrder() == True:
			self.setSortOrderAscending()
		else:
			self.setSortOrderDescending()
		return

	def getSortOrder(self):
		"get current sort order with True if descending"
		return self.sortOrderDescending

	# search entry

	def addEntry(self, entry):
		"registers the given entry, and returns its document id"
		entryId = self.getEmptyId()
		entry.setEntryId(entryId)
		self.entryList.append(entry)
		return entryId

	def isInEntryList(self, entryId):
		"returns True if document with entryId was registered"
		value = False
		for entry in self.entryList:
			if entry.getEntryId() == entryId:
				value = True
				break
		return value

	def removeEntry(self, entryId):
		"remove document with entryId from list of entries"
		newEntryList = []
		for entry in self.entryList:
			if entry.getEntryId() != entryId:
				newEntryList.append(entry)
		self.entryList = newEntryList
		return

	def clearEntryList(self):
		"unregister all documents -- clear the entry list"
		self.entryList = []
		return

	def countEntryList(self):
		"counts the registered documents, and returns its number"
		return len(self.entryList)

	def getEntryList(self):
		"return full list of registered documents"
		entryList = []
		for entry in self.entryList:
			entryList.append(entry.getEntry())
		return entryList

	def getEmptyId(self):
		"returns a new, still unused document id"
		entryId = 0
		idList = []
		for entry in self.entryList:
			idList.append(entry.getEntryId())

		if (len(idList)):
			entryId = max(idList) + 1

		return entryId

	# sort entry list

	def sortEntryList(self, entryList):
		"sort entry list ascending, or descending"
		if len(entryList) == 0:
			return []
		else:
			return sorted(entryList, key=lambda entry: entry[0], reverse = self.getSortOrder())

	# merge lists

	def mergeLists(self, *lists):
		"merge lists of words"

		newlist = {} 	# start with an empty list

		for currentList in lists:
			keyList = currentList.keys()
			for item in keyList:
				# assume a new item
				frequency = 0
				
				# item already in newlist?
				if newlist.has_key(item):
					frequency = newlist[item]

				frequency += currentList[item]
				newlist[item] = frequency

		return newlist

	def mergeListsIdf(self, *lists):
		"merge lists of words for calculating idf"

		newlist = {} 	# start with an empty list

		for currentList in lists:
			keyList = currentList.keys()
			for item in keyList:
				# assume a new item
				frequency = 0
				
				# item already in newlist?
				if newlist.has_key(item):
					frequency = newlist[item]

				frequency += 1
				newlist[item] = frequency

		return newlist

	# stop list

	def setStopList(self, stopList):
		"fill the stop list with the given values"
		self.stopList = stopList
		return

	def getStopList(self):
		"return the current stop list"
		return self.stopList

	def extendStopList(self, itemList):
		"extends the current stop list with the given items"
		for item in itemList:
			if not item in self.stopList:
				self.stopList.append(item)
		return

	def reduceStopList(self, itemList):
		"reduces the current stop list by the given items"
		for item in itemList:
			if item in self.stopList:
				self.stopList.remove(item)
		return

	# phonetic comparisons

	def comparePhoneticCode(self, entry1, entry2):
		"compares two entries of phonetic codes and returns the number of exact matches"
		matches = 0
		
		for item in entry1.keys():
			if entry2.has_key(item):
				if entry1[item] == entry2[item]:
					matches += 1
		
		return matches

	def comparePhoneticCodeLists(self, query, document):
		"compare phonetic codes of a query and a single document"
		total = 0
		for entry in query:
			codes = query[entry]
			#print entry
			#print codes
			
			for entry2 in document:
				codes2 = document[entry2]
				#print entry2
				#print codes2
				matches = self.comparePhoneticCode(codes, codes2)
				total += matches
		return total

	def searchByPhoneticCode(self, query):
		"find all the documents matching the query in terms of phonetic similarity"
		matchList = {}
		for entry in self.getEntryList():
			entryId = entry.getEntryId()
			matches = self.comparePhoneticCodeLists(query, entry)
			matchList[entryId] = matches
		return matchList

	# term frequency for all registered search entries

	def tf(self):
		"term frequency for the list of registered documents"
		occurency = {}
		for entry in self.entryList:
			tf = entry.data.tf()
			occurency = self.mergeLists(occurency, tf)

		return occurency
			
	def tfStop(self):
		"term frequency with stop list for the list of registered documents"
		occurency = {}
		for entry in self.entryList:
			tfStop = entry.data.tfStop(self.stopList)
			occurency = self.mergeLists(occurency, tfStop)

		return occurency

#	def tfRelation(self, pattern, document):
#		keysPattern = pattern.keys()
#		keysDocument = document.keys()
#		identicalKeys = list(set(keysPattern.keys()) & set(keysDocument.keys())
#		
#		total = 0
#		for item in identicalKeys:
#			total = total + pattern[item] + document[item]
#		return

	def idf (self, wordList):
		"calculates the inverse document frequency for a given list of terms"

		key = wordList.keys()
		documents = self.countEntryList()

		for item in key:
			frequency = wordList[item]

			# calculate idf = ln(N/n):
			# N=number of documents
			# n=number of documents that contain term
			idf = math.log(documents/frequency)

			wordList[item] = idf

		return wordList

	# evaluate and compare descriptors

	def compareDescriptors (self, request, document):
		"returns the degree of equality between two descriptors (often a request and a document)"
	
		compareBinary = self.compareDescriptorsBinary(request, document)
		compareFuzzy = self.compareDescriptorsFuzzy(request, document)
		compareKnn = self.compareDescriptorsKNN(request, document)

		result = {
			'binary': compareBinary, 
			'fuzzy': compareFuzzy,
			'knn': compareKnn
		}
		return result

	def compareDescriptorsBinary(self, request, document):
		"binary comparison"

		# request, document: document descriptors
		# return value: either True for similarity, or False

		# define return value
		equality = 0

		# calc similar descriptors
		itemsRequest = request.getDescriptorList()
		itemsDocument = document.getDescriptorList()
		if set(itemsRequest) & set(itemsDocument) == set(itemsRequest):
			equality = 1
		return equality

	def compareDescriptorsFuzzy(self, request, document):
		"fuzzy comparison"

		# request, document: lists of descriptors
		# return value: float, between 0 and 1

		# define return value
		equality = 0

		# get number of items
		itemsRequest = request.getDescriptorList()
		itemsDocument = document.getDescriptorList()

		# calc similar descriptors
		similarDescriptors = len(set(itemsRequest) & set(itemsDocument))

		# calc equality
		equality = float(similarDescriptors) / float ((math.sqrt(len(itemsRequest)) * math.sqrt(len(itemsDocument))))

		return equality

	def compareDescriptorsKNN(self, request, document):
		"k-Nearest Neighbour algorithm"

		firstList = request
		otherList = document
		
		globalDistance = float(0)
		for item in firstList.getDescriptorList():
			firstValue = float(firstList.getDescriptorValue(item))
			otherValue = float(otherList.getDescriptorValue(item))
			i = float(firstValue - otherValue)
			localDistance = float(i * i)
			globalDistance = globalDistance + localDistance
		# end for

		for item in otherList.getDescriptorList():
			otherValue = float(otherList.getDescriptorValue(item))
			firstValue = 0
			if item in firstList.getDescriptorList():
				continue	# don't count again
			localDistance = float(otherValue * otherValue)
			globalDistance = globalDistance + localDistance
		# end for
		
		kNN = math.sqrt(globalDistance)

		return kNN

	def calculateRetrievalStatusValue(d, p, q):
		"calculates the document weight for document descriptors"

		# d: list of existance (1) or non-existance (0)
		# p, q: list of probabilities of existance (p) and non-existance (q)

		itemsP = len(p)
		itemsQ = len(q)
		itemsD = len(d)

		if ((itemsP - itemsQ) <> 0):
			# different length of lists p and q
			return 0

		if ((itemsD - itemsP) <> 0):
			# different length of lists d and p
			return 0

		rsv = 0

		for i in range(itemsP):
			eqUpper = float(p[i]) / float(1-p[i])
			eqLower = float(q[i]) / float(1-q[i])

			value = float(d[i] * math.log (eqUpper / eqLower))
			rsv += value

		return rsv

	# search strategy

	def setSearchStrategy(self, fullTextWeight, advancedWeight):
		"adjust the current search strategy"
		self.searchStrategy = {
			"fulltextsearch": fullTextWeight,
			"advancedsearch": advancedWeight
		}
		return

	def getSearchStrategy(self):
		"returns the current search strategy"
		return self.searchStrategy
	
	# search

	def search(self, pattern):
		"combines both full text, and advanced search"
		result = []
		
		searchStrategy = self.getSearchStrategy()
		fullTextWeight = searchStrategy["fulltextsearch"]
		advancedWeight = searchStrategy["advancedsearch"]

		if fullTextWeight:
			result = self.fullTextSearch(pattern)

		if advancedWeight:
			resultAdvancedSearch = self.advancedSearch(pattern)
			if not len(result):
				result = resultAdvancedSearch
			else:
				for item in resultAdvancedSearch:
					weightAVS, hitsAVS, entryIndexAVS = item

					for i in xrange(len(result)):
						entry = result[i]
						weightFTS, hitsFTS, entryIndexFTS = entry
						if entryIndexAVS == entryIndexFTS:
							weight = weightAVS + weightFTS
							hits = hitsAVS + hitsFTS
							result[i] = (weight, hits, entryIndexAVS)
							break
		
		return self.sortEntryList(result)

	def fullTextSearch(self, pattern):
		"full text search for the registered documents"

		searchStrategy = self.getSearchStrategy()
		fullTextWeight = searchStrategy["fulltextsearch"]

		# search for the given search pattern
		# both data and query are multiline objects
		originalQuery = pattern.getText()
		query = ''.join(originalQuery)

		result = []
		for entry in self.entryList:
			originalData = entry.getText()
			data = ''.join(originalData)

			hits = data.count(query)

			# set return value
			entryId = entry.getEntryId()
			value = fullTextWeight * hits
			result.append((value, hits, entryId))

		# sort the result according to the sort value
		result = self.sortEntryList(result)

		return result

	def advancedSearch(self, pattern):

		searchStrategy = self.getSearchStrategy()
		advancedWeight = searchStrategy["advancedsearch"]

		tfPattern = pattern.data.tf()
		digramPattern = pattern.data.getNgramsByParagraph(2)
		trigramPattern = pattern.data.getNgramsByParagraph(3)
		phoneticPattern = pattern.getPhoneticCode()
		descriptorsPattern = pattern.getKeywords()

		result = []
		for entry in self.entryList:

			# calculate tf
			tfEntry = entry.data.tf()

			# calculate digrams
			digramEntry = entry.data.getNgramsByParagraph(2)
			digramValue = entry.data.compareNgramLists(digramEntry, digramPattern)

			# calculate trigrams
			trigramEntry = entry.data.getNgramsByParagraph(3)
			trigramValue = entry.data.compareNgramLists(trigramEntry, trigramPattern)

			# phonetic codes
			phoneticEntry = entry.getPhoneticCode()
			phoneticValue = self.comparePhoneticCodeLists(phoneticPattern, phoneticEntry)

			# descriptor comparison
			descriptorsEntry = entry.getKeywords()
			desc = self.compareDescriptors (descriptorsPattern, descriptorsEntry)
			descValue = desc['binary']*0.3 + desc['fuzzy']*0.3 + desc['knn']*0.4

			hits = 0
			value = digramValue * 0.25
			value += trigramValue * 0.25
			value += phoneticValue * 0.25
			value += descValue * 0.25

			# set return value
			entryId = entry.getEntryId()
			value = advancedWeight * value
			result.append((value, hits, entryId))

		return result
