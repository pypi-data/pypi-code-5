#!/usr/bin/python

# pyversions -- Library that implements Python like methods in JavaScript.
#
# Copyright (c) 2014, Web Heroes Inc.
#
# This file is part of pyversions
#
# pyversions is free software: you can redistribute it and/or modify
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

from collections import OrderedDict

class Version_dict(OrderedDict):
    
    def __init__( self ):
        super(Version_dict, self).__init__()

    def __setitem__( self, name, value ):
        super(Version_dict, self).__setitem__( name, value )
        self.sort()

    def __call__( self, start=None, stop=None ):
        return self.slice( start, stop )

    def slice( self, start=None, stop=None ):
        remove_start	= False
        remove_stop	= False

        if start is not None and start not in self:
            remove_start	= True
            self[start]		= True
        if stop is not None and stop not in self:
            remove_stop		= True
            self[stop]		= True
        
        found			= False
        for v, name in self.items():
            if start is not None and not found:
                if v == start:
                    if remove_start:
                        del self[start]
                    else:
                        yield (v, name)
                    found	= True
                continue

            if stop is not None and v == stop:
                if remove_stop:
                    del self[stop]
                else:
                    yield (v, name)
                break
            yield (v, name)

    def sort( self ):
        keys		= self.keys()
        def k(v):
            if v.isdigit():
                return int(v)
            else:
                try:
                    # v and r could both be either a int or a str at this point.
                    v,r	= v.split('-', 2)
                    if not v.isdigit():
                        v		= str(ord(v))
                    v		       += "."
                    if r.isdigit():
                        v	       += "%05d" % int(r)
                    else:
                        for i in r:
                            if i.isdigit():
                                n	= int(i)
                            else:
                                n	= ord(i)
                            v      += "%05d" % n
                    v	= float(v)
                except Exception as exc:
                    pass
                return v
        keys.sort( key=lambda s: map(k, s.split('.')) )
        for k in keys:
            v		= self[k]
            del self[k]
            super(Version_dict, self).__setitem__( k, v )
        