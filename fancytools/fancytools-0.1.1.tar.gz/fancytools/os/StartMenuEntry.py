# -*- coding: utf-8 -*-
import os
#import sys
#import site
import stat

from isAdmin import isAdmin
#print isAdmin
class _LinuxStartMenuEntry(object):

	def __init__(self, name, target,
				icon, directory,
				version, description, categories):
		self.name = name
		self.icon = icon
		self.directory = directory
		self.version = version
		self.categories = categories
		self.description = description
		self.target = target
		if isAdmin():
			self.filename = '/usr/share/applications/%s.desktop' %name
		else:
			self.filename = os.path.expanduser("~")+ '/.local/share/applications/%s.desktop' %name


	def create(self):
		#create starter
		d = os.path.dirname(self.filename)
		if not os.path.exists(d):
			os.mkdir(d)
		
		with open(self.filename, 'w') as f:
			text = '''
[Desktop Entry]
Version=%s
Name=%s
Comment=%s
Icon=%s
Exec=python %s
Terminal=false
Type=Application
Categories=Application;Science;Graphics;Office;
MimeType=PYZ''' %(
		self.version,
		self.name,
		self.description, self.icon,self.target)
			#enable unicode-characters ('ä' etc.) and write to file
			f.write( text.encode('UTF-8') )
		os.chmod(self.filename, os.stat(self.filename).st_mode | stat.S_IEXEC)


	def remove(self):
		if ( os.path.exists(self.filename) ) :
			os.remove(self.filename)



class _WindowsStartMenuEntry:

	def __init__(self, name, target,
				icon, directory,
				version, description, categories):
		self.name = name
		self.icon = icon
		self.directory = directory
		import win32com.client

		self.sh = win32com.client.Dispatch( "WScript.Shell" )
		if isAdmin():
			folder = "AllUsersPrograms"
		else:
			folder = "StartMenu"
		self.path = self.sh.SpecialFolders(folder)
		assert( os.path.isdir(self.path) )

		if self.directory:
			self.path= os.path.join( self.path, self.directory)
		self.lnkPath = os.path.join( self.path, name + ".lnk" )
		self.lnk = self.sh.CreateShortcut( self.lnkPath )
		self.lnk.TargetPath = target


	def create(self):
		#create shortcut group is not existent:
		if ( not os.path.isdir(self.path) ) :
			os.makedirs(self.path)
		if self.icon:
			if not self.icon.lower().endswith('.ico'):
				raise ValueError('only icons of type ICO are accepted')
			self.lnk.IconLocation = self.icon
		self.lnk.Save()


	def remove(self):
		if ( os.path.exists(self.lnkPath) ) :
			os.remove(self.lnkPath)
			#if shortcut-group is empty now: delete it
			if self.directory and not os.listdir(self.path):
				os.removedirs(self.path)



class StartMenuEntry(object):
	'''
	this class creates a shortcut for a given target in the startmenu of the
	used os depending either systemwide or user specific
	
	>>> entry = StartMenuEntry('myLittleTest', 'www.python.org')
	>>> entry.create()
	>>> raw_input('Now look for the entry in your start menu and press Enter if you found it')
	>>> entry.remove()
	
	'''
	def __init__(self, name, target,
				icon=None,directory=None,
				version='-', description='', categories=''):

		if os.name == 'posix': #for linux-systems
			self.__class__ = _LinuxStartMenuEntry
		elif os.name == 'nt':
			self.__class__ = _WindowsStartMenuEntry
		else:
			raise OSError('creating start menu entries is not implemented for mac at the moment')

		self.__init__(name, target, icon, directory, version, description, categories)





#name = "Visit Microsoft's website"
#target = "http://www.microsoft.com"
#directory = "My Start Menu Shortcuts"

#_WindowsStartMenuEntry(name,target,
	#icon='C:\Windows\System32\PerfCenterCpl.ico').create()

			#iconPath = os.path.join(self.instpath, self.identity.LOGO)#'%s/nIOp/media/logo.svg' %path

#self.identity.LAUNCHER_FILE
