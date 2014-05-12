# -*- coding: utf-8 -*-
import os
import shutil

class PathStr(str):

	@staticmethod
	def home():
		return PathStr(os.path.expanduser("~"))

	def join(self, *args):
		return PathStr(os.path.join(self,*args))


	def exists(self):
		return os.path.exists(self)


	def abspath(self):
		return PathStr(os.path.abspath(self))


	def load(self, size):
		if os.path.exists(self):
			return eval( open(self).read(size) )

	def dirname(self):
	#	if os.path.isdir(self):
	#		return self
		return PathStr(os.path.dirname(self))





	def basename(self):
		return PathStr(os.path.basename(self))

	def move(self, dst):
		shutil.move(self, dst)
		self = PathStr(dst).join(self.basename())
		return self

	def mkdir(self, dname):
		n = self.join(dname)
		if not n.exists():
			os.mkdir(n)
		return n

	def remove(self, name=None):
		f = self
		if name:
			f = self.join(name)
		try:
			os.remove(f)
		except OSError:
			os.rmdir(f)

	def filetype(self):
		if '.' in self:
			return self.split('.')[-1]
		return ''

	def isfile(self):
		return os.path.isfile(self)

	def isdir(self):
		return os.path.isdir(self)


	def listdir(self):
		if os.path.isdir(self):
			d = self
		else:
			d = os.path.dirname(self)
		return os.listdir(d)


	def __iter__(self):
		#TODO: iter and listdir as generator object
		if self.exists():
			return iter(self.listdir())
		return iter([])




	#def __iter__(self):
		##TODO: iter and listdir as generator object
		#self._n = -1
		#if self.exists():
			#self._l = self.listdir()
		#else:
			#self._l =[]
		#return self
##			return os.walk(self.dirname())



	#def next(self):
		#self._n += 1
		#return self._l[self._n]
		#