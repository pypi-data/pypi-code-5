#!/usr/bin/python

# pyversioning-mysql -- Library that implements Python like methods in JavaScript.
#
# Copyright (c) 2014, Web Heroes Inc.
#
# This file is part of pyversioning-mysql
#
# pyversioning-mysql is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__	import print_function
from version	import Version_dict
from bashutils.colors	import color_text as ctext

import MySQLdb
import MySQLdb.cursors

import os, imp

def white(text):
    return ctext(text, color="white")

class MySQL_database(object):
    
    def __init__( self,
                  host		= "localhost",
                  port		= 3306,
                  user		= None,
                  password	= None,
                  packages	= None, ):

        assert packages is not None, "packages argument must be a list of package file paths. (preferably named with the .pack extension)"

        self._conn	= MySQLdb.connect( host		= host,
                                           port		= port,
                                           user		= user,
                                           passwd	= password,
                                           cursorclass	= MySQLdb.cursors.DictCursor, )
        self._cursor	= self._conn.cursor()
        self.quiet	= False

        # From:	<path>/<version>_<name>.<ext>
        # To:	self[<version>]	= ( <name>, <path> )
        self._packs		= Version_dict()
        for pack in packages:
            f, ext		= os.path.splitext( os.path.basename( pack ))
            v, name		= f.split('_', 1)
            self._packs[v]	= ( pack, name )
        
    def packages( self, start=None, stop=None ):
        return self._packs.slice( start, stop )
        
    def upgrade( self, version ):
        packages		= self._packs.slice( stop=version )
        for version in packages.keys():
            self.install(version)
        return packages
        
    def downgrade( self, version ):
        packages		= self._packs.slice( start=version )
        packages.pop(version, None)
        packages.reverse()
        for version in packages.keys():
            self.uninstall(version)
        return packages

    def load( self, version ):
        assert version in self._packs, "There is no package with version %s" % (version,)
        path, name		= self._packs[version]
        pack			= imp.load_source(name, path)
        os.remove( path+'c' ) # remove compiled file
        return pack, name

    def install( self, version ):
        pack, name		= self.load( version )
        if not pack.check( self._conn, self._cursor ):
            self.quiet or print( white("""Installing: v{: <8}   -- {:<40}""".format( version,
                                                                                   name.replace('-', ' ').title() )))
            pack.upgrade( self._conn, self._cursor )

    def uninstall( self, version ):
        pack, name		= self.load( version )
        if pack.check( self._conn, self._cursor ):
            self.quiet or print( white("""Uninstalling: v{: <8} -- {:<40}""".format( version,
                                                                                   name.replace('-', ' ').title() )))
            pack.downgrade( self._conn, self._cursor )

