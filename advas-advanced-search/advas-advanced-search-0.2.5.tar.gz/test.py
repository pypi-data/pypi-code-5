# -*- coding: utf-8 -*-

from advancedsearch import AdvancedSearch
from entry import Entry
from advasio import AdvasIo
from descriptors import Descriptors

from phonetics import Phonetics
from stemmer import Stemmer
from advas import Advas

# define global settings
encoding = "utf-8"

# --- preprocessing ---

# - load vocabulary
# - load topic dependencies

# - prepare search entries
keywordList = {'Essen': 0.5, 'Literatur': 0.4}
keywords = Descriptors(keywordList)

classificationList = {}
classification = Descriptors(classificationList)

searchEntry1 = Entry(["Stattdessen gab es Eintopf."], encoding, keywords, classification)
searchEntry2 = Entry(["Das Krankenhaus am Rande der Grossstadt"], encoding, keywords, classification)
searchEntry3 = Entry(["was haben wir gelacht,\n", "als wir an dich gedacht"], encoding, keywords, classification)
searchEntry4 = Entry(["das ist ein test, nicht wahr.\n", "Oder doch?"], encoding, keywords, classification)

filename5 = "lausanne.txt"
keywords5 = Descriptors({'Lausanne': 0.9, 'Vaud': 0.9})
file5 = AdvasIo(filename5, encoding)
success = file5.readFileContents()
if not success:
	print "Fehler beim Lesen der Datei: ", filename5
else:
	contents = file5.getFileContents()
	searchEntry5 = Entry(contents, encoding, keywords5, classification)

# - prepare search request
keywordsRequest = Descriptors({'Lausanne': 0.5, 'Vaud': 0.75})
pattern = Entry(["Lausanne"], encoding, keywords, classification)

# - setup search engine
searchEngine = AdvancedSearch()

# - register search entries
entryId1 = searchEngine.addEntry(searchEntry1)
entryId2 = searchEngine.addEntry(searchEntry2)
entryId3 = searchEngine.addEntry(searchEntry3)
entryId4 = searchEngine.addEntry(searchEntry4)

if success:
	entryId5 = searchEngine.addEntry(searchEntry5)

# --- display entry list

#print searchEngine.getEntryList()

# --- search ---

result = searchEngine.search(pattern)

# --- post-processing ---

# --- output search result ---

for item in result:
	print "Bewertung  : ", item[0]
	print "Suchtreffer: ", item[1]
	print "Eintrags-ID: ", item[2]
	print " "

# --- other functions and tests ---

#searchEntry3 = Entry("awk", encoding, keywords, classification)
#entryId3 = searchEngine.addEntry(searchEntry3)
#searchEngine.removeEntry(entryId1)
print searchEngine.getEntryList()
#
#result = searchEngine.search(pattern)
#print result

#keywordList1 = {'Essen': 0.8, 'Literatur': 0.1}
#keywords1 = Descriptors(keywordList1)

#keywordList2 = {'Feuerwehr': 0.5, 'Literatur': 0.1}
#keywords2 = Descriptors(keywordList2)

#desc = searchEngine.compareDescriptors (keywords1, keywords2)
#print desc['binary']
#print desc['fuzzy']
#print desc['knn']

# - term frequency for single entries

#print searchEntry3.data.tf()
#print searchEntry4.data.tf()

# - use stop list per entry
#stopList = ["der", "die", "das"]
#print searchEntry4.data.tfStop(stopList)

# - use global stop list
#searchEngine.setStopList(stopList)

# - tf for all registered entries
#tf = searchEngine.tf()

# - tf with stop list for all registered entries
#tfStop = searchEngine.tfStop()

# - idf for all registered entries
#idf = searchEngine.idf(tf)

# - two-grams

# - trigrams
#trigram3 = searchEntry3.data.getNgramsByParagraph(3)
#trigram4 = searchEntry4.data.getNgramsByParagraph(3)
#trigram5 = searchEntry5.data.getNgramsByParagraph(3)
#trigramPattern = pattern.data.getNgramsByParagraph(3)
#print trigram3
#print trigram5
#print trigramPattern
#print searchEngine.compareNgramLists(trigram5, trigramPattern)

# - phonetic codes
# -- soundex
#print searchEntry3.data.soundex()
#print searchEntry5.data.soundex()

# -- metaphone
#print searchEntry3.data.metaphone()
#print searchEntry5.data.metaphone()

# -- nysiis
#print searchEntry3.data.nysiis()
#print searchEntry5.data.nysiis()

# -- caverphone
#print searchEntry3.data.caverphone()
#print searchEntry5.data.caverphone()

# -- phonetic code
#print searchEntry3.data.phoneticCode()

#query = pattern.getPhoneticCode()
#document = searchEntry5.getPhoneticCode()

#print query
#print document
#print " "
#print pattern.data.comparePhoneticCodeLists(query, document)

#varList = ["halten", "hielt", "gehalt", "haltbar"]
#so = Stemmer("")
#print so.successorVariety ("gehalten", varList)

#varObject = Phonetics("")
#sv = varObject.calcSuccVarietyList(varList)
#print sv
#svm = varObject.calcSuccVarietyMerge(sv)
#print svm
#print varObject.calcSuccVarietyCount(svm)

#text = Advas(["die Kinder freuen sich über die Kastanien"], "")
#keywordList = ["die", "der", "das", "sich"]
#print text.isLanguageByKeywords (keywordList)
#text = Advas(["Schule"], "")
#print text.getSynonyms("/home/frank/projekte/openthesaurus/openthesaurus.txt", "")
#print text.isSynonymOf("Bildungszentrum", "/home/frank/projekte/openthesaurus/openthesaurus.txt", "")

# -- ngram stemmer
stemmerObject = Stemmer("")
print stemmerObject.ngramStemmer(["halten", "hielt", "halter", "halt", "gehalten"], 2, 0.4)


