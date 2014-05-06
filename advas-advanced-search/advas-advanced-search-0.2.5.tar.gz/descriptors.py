# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# module dealing with document descriptors
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

class Descriptors:

	def __init__(self, descriptorList):
		self.data = {}
		for item in descriptorList:
			self.addDescriptor(item, descriptorList[item])
		return

	def countDescriptors(self):
		return len(self.data)

	def addDescriptor(self, descriptor, value):
		if descriptor in self.data:
			return False
		else:
			self.data[descriptor] = value
		return True

	def removeDescriptor(self, descriptor):
		if descriptor in self.data:
			del self.data[descriptor]
			return True
		else:
			return False

	def updateDescriptor(self, descriptor, value):
		if descriptor in self.data:
			self.data[descriptor] = value
			return True
		else:
			return False

	def increaseDescriptor(self, descriptor, value):
		if descriptor in self.data:
			self.data[descriptor] += value
			return True
		else:
			return False

	def decreaseDescriptor(self, descriptor, value):
		if descriptor in self.data:
			self.data[descriptor] -= value
			return True
		else:
			return False

	def getDescriptorPair(self, entry):
		if entry in self.getDescriptorList():
			return [entry, self.data[entry]]
		else:
			return None
			
	def getDescriptorValue(self, entry):
		if entry in self.getDescriptorList():
			return self.data[entry]
		else:
			return 0

	def getDescriptorList(self):
		return self.data.keys()
		
	def getDescriptorListValues(self):
		return self.data.values()
