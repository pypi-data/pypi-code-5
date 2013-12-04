#!/usr/bin/python

# Copyright (C) 2012-2013 Cyrille Defranoux
#
# This file is part of Pyknx.
#
# Pyknx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyknx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyknx. If not, see <http://www.gnu.org/licenses/>.
#
# For any question, feature requests or bug reports, feel free to contact me at:
# knx at aminate dot net

import sys
import re
import getopt
import time
from xml.dom.minidom import parseString
from threading import *
from pyknx import tcpsocket, logger

class Linknx:

	"""
	The wrapper of an instance of Linknx.

	This class eases access to Linknx functionalities: it can retrieve objects (see getObject() and getObjects()), or configuration.
	"""

	class InvalidObjectIdException(Exception):
		""" The object id is not valid in the Linknx instance. """
		def __init__(self, objectId):
			self._objectId = objectId

		def __str__(self):
			return 'Object ' + self._objectId + ' does not exist.'

	def __init__(self, hostname='localhost', port=1028):
		""" Initialize a Linknx wrapper. """
		self._host = hostname
		self._port = port
		self._config = None
		self._objectConfig = None
		self._objects = {}

	@property
	def host(self):
		return self._host

	@property
	def port(self):
		return self._port

	@property
	def config(self):
		"""
		Get the raw XML configuration currently used by the running Linknx instance.

		See objectConfig property for an alternative of these raw data.

		"""

		if self._config is None:
			xmlConfig = self.sendMessage("<read><config></config></read>").getElementsByTagName('read')[0]
			self._config = xmlConfig.getElementsByTagName('config')[0]

		return self._config

	@property
	def objectConfig(self):
		""" Return a dictionary of the configuration of each Linknx object. Keys are object ids, values are ObjectConfig instances. """
		if not self._objectConfig:
			objectsConfigNode = self.config.getElementsByTagName('objects')[0]
			self._objectConfig = {} # key is objectId, value is an ObjectConfig
			for objectConfigNode in objectsConfigNode.getElementsByTagName('object'):
				objectConfig = ObjectConfig(objectConfigNode)
				self._objectConfig[objectConfig.id] = ObjectConfig(objectConfigNode)

		return self._objectConfig

	def waitForRemoteConnectionReady(self):
		"""
		Wait for Linknx's XML server to accept incoming connections.

		This method should be called if unsure about when the Linknx has been started. It may take some time to get ready.
		This method attempts to connect to Linknx during 10 seconds and raises an Exception if Linknx still is unreachable after this delay.

		"""
		# Ask for config.
		logger.reportInfo('Start connecting to linknx.')
		attemptId = 0
		maxAttemptCount = 10
		while attemptId < maxAttemptCount:
			attemptId += 1
			try:
				conf = self.config

				# Linknx is ready if we reach this point.
				logger.reportInfo('Linknx is up and ready, let\'s start.')
				return
			except Exception as e:
				logger.reportInfo('Linknx is not yet ready...  (attempt {0}/{1})'.format(attemptId, maxAttemptCount))
				time.sleep(1)

		raise Exception('Linknx is not reachable.')

	def getObject(self, id):
		""" Get the object of given identifier. """
		obj = self._objects.get(id)
		if obj is None:
			obj = Object(id, self)
			self._objects[id] = obj
		return obj

	def getObjects(self, pattern='.*'):
		""" Get the objects whose identifiers match the given regex pattern. Default pattern matches all identifiers, thus calling getObjects() returns all objects. """
		regex = re.compile(pattern)
		objects = []
		for id in self.objectConfig.iterkeys():
			if regex.search(id) is None: continue
			objects.append(self.getObject(id))
		return objects

	def _getErrorFromXML(self, answer):
		errorMessage = ""
		for child in answer.childNodes:
			if child.nodeType == child.TEXT_NODE:
				errorMessage += child.data
		return errorMessage

	def sendMessage(self, message):
		"""
		Sends an XML message to Linknx.

		This function is implemented mainly for internal purposes. The end user is unlikely to call it directly.
		message -- An XML request that follows Linknx XML protocol.
		Returns an XML document that corresponds to Linknx answer.

		"""
		# logger.reportDebug('Sending message to linknx: ' + message)
		s = tcpsocket.Socket()
		s.connect((self._host, self._port))
		try:
			answer = s.sendData(message)
			# logger.reportDebug('Linknx answered ' + answer)
			return parseString(answer[0:answer.rfind(chr(4))])
		finally:
			s.close()

class ObjectConfig:
	def __init__(self, configNode):
		"""	Configuration of an object in Linknx. """
		self.id = configNode.getAttribute('id')
		self.xml = configNode
		self.type = configNode.getAttribute('type')
		self.gad = configNode.getAttribute('gad')
		self.callback = configNode.getAttribute('pyknxcallback')
		self.init = configNode.getAttribute('init') if configNode.hasAttribute('init') else 'request'
		self.flags = configNode.getAttribute('flags') if configNode.hasAttribute('flags') else 'cwtu'
		firstTypeDigit = self.type[0:self.type.find('.')]
		if firstTypeDigit == '1':
			self.typeCategory = 'bool'
		elif firstTypeDigit in ['5', '6', '7', '8', '9', '12', '13']:
			if self.type in ['5.001', '5.003', '9.xxx']:
				# 5.001 and 5.003 are actually float values encoded on 256
				# levels between 0-100 or 0-360.
				self.typeCategory='float'
			else:
				self.typeCategory = 'int'
		elif firstTypeDigit == '16':
			self.typeCategory='string'
		else:
			logger.reportWarning('Object ' + self.id + ' has an unsupported type ' + self.type)
			self.typeCategory = 'unknown'

	# @property
	# def defaultValue(self):
		# """ Return the default value of the object. """
		# if self.type == 'bool':
			# return False
		# elif self.type == 'int':
			# return 0
		# elif self.type == 'float':
			# return 0.0
		# elif self.type == 'string':
			# return ''
		# else:
			# return None

class Object(object):

	""" Linknx object. """

	def __init__(self, id, linknx):
		"""
		Initialize an object from Linknx.

		id -- Identifier of the object. Corresponds to the id attribute in XML configuration.
		linknx -- Linknx instance that provides the object.
		"""
		self._id = id
		self._linknx = linknx
		if not linknx.objectConfig.has_key(id):
			raise Linknx.InvalidObjectIdException(id)

		self._objectConfig = linknx.objectConfig[id]

	@property
	def id(self):
		""" Object identifier. This is the id attribute in XML configuration. """
		return self._id

	@property
	def gad(self):
		""" Group Address of the object. This is the gad attribute in XML configuration. """
		return self._objectConfig.gad

	@property
	def linknx(self):
		""" Return the Linknx instance that provides the object. """
		return self._linknx

	@property
	def xml(self):
		""" Return the xml element corresponding to this object in Linknx configuration. """
		return self._objectConfig.xml

	@property
	def type(self):
		""" Return the string corresponding to the type attribute in XML configuration. """
		return self._objectConfig.type

	@property
	def value(self):
		""" Read object's value from linknx. """
		message='<read><objects><object id="' + self._id + '"/></objects></read>'

		answerDom = self._linknx.sendMessage(message)

		readNodes = answerDom.getElementsByTagName("read")
		status = readNodes[0].getAttribute("status")
		valueStr = None
		if status == "success":
			objectValues = {}
			objectsNodes = readNodes[0].getElementsByTagName("objects")
			objectNodes = objectsNodes[0].getElementsByTagName("object")
			for objectNode in objectNodes:
				objectId = objectNode.getAttribute("id")
				objectValue = objectNode.getAttribute("value")
				objectValues[objectId] = objectValue
			valueStr = objectValues[self._id]
		else:
			raise Exception(self._linknx._getErrorFromXML(readNodes[0]))

		if self._objectConfig.typeCategory == 'bool':
			return valueStr in ['on', '1']
		elif self._objectConfig.typeCategory == 'int':
			return int(valueStr)
		elif self._objectConfig.typeCategory == 'float':
			return float(valueStr)
		else:
			return valueStr

	@value.setter
	def value(self, objValue):
		""" Write object's value to linknx. """
		# Convert value to the linknx format.
		logger.reportDebug('Attempting to set value of {0} to {1}'.format(self._id, objValue))
		if self._objectConfig.typeCategory == 'bool':
			if isinstance(objValue,bool):
				objectValue = 'on' if objValue else 'off'
			else:
				objValueStr = str(objValue).lower()
				if objValueStr in ['true', 'on', 'yes', '1']:
					objectValue = 'on'
				elif objValueStr in ['false', 'off', 'no', '0']:
					objectValue = 'off'
				else:
					raise Exception('For object {1}: Unable to convert {0} to boolean.'.format(objValue, self._id))
		elif self._objectConfig.typeCategory == 'int':
			objectValue = str(objValue)
		elif self._objectConfig.typeCategory == 'float':
			objectValue = str(objValue)
		elif self._objectConfig.typeCategory == 'string':
			objectValue = str(objValue)
		else:
			raise Exception('Unsupported type ' + self._objectConfig.typeCategory)

		if not objValue is objectValue:
			logger.reportDebug('Value has been converted to ' + str(objectValue))

		message='<write><object id="' + self._id + '" value="' + objectValue + '"/></write>'
		answerDom = self._linknx.sendMessage(message)
		writeNodes = answerDom.getElementsByTagName("write")
		status = writeNodes[0].getAttribute("status")
		if status != "success":
			raise Exception(self._linknx._getErrorFromXML(writeNodes[0]))

	def __repr__(self):
		return self.id

	def __str__(self):
		return self.id
