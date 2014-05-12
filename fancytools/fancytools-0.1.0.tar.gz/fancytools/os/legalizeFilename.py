# -*- coding: utf-8 -*-
import string, unicodedata

def legalizeFilename(filename):
	validFilenameChars = "/-_.%s%s" % (string.ascii_letters, string.digits)
	replaceDict = {
		" ":"-",
		u"ä":"ae",
		u"ö":"oe",
		u"ü":"ue",
		u'µ':'mue'}
	filename = unicode(filename)
	for key in replaceDict:
		filename.replace(key, replaceDict[key])
	cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
	return ''.join(c for c in cleanedFilename if c in validFilenameChars)[:255]


