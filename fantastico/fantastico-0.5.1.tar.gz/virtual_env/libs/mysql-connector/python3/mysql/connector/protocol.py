# MySQL Connector/Python - MySQL driver written in Python.
# Copyright (c) 2009, 2013, Oracle and/or its affiliates. All rights reserved.

# MySQL Connector/Python is licensed under the terms of the GPLv2
# <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>, like most
# MySQL Connectors. There are special exceptions to the terms and
# conditions of the GPLv2 as it is applied to this software, see the
# FOSS License Exception
# <http://www.mysql.com/about/legal/licensing/foss-exception.html>.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""Implementing the MySQL Client/Server protocol
"""

import struct
from decimal import Decimal

try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

from .constants import (FieldFlag, ServerCmd)
from . import (errors, utils)

class MySQLProtocol(object):
    def _scramble_password(self, passwd, seed):
        """Scramble a password ready to send to MySQL"""
        hash4 = None
        try: 
            hash1 = sha1(passwd).digest()
            hash2 = sha1(hash1).digest() # Password as found in mysql.user()
            hash3 = sha1(seed + hash2).digest()
            xored = [ h1 ^ h3 for (h1,h3) in zip(hash1, hash3) ]
            hash4 = struct.pack('20B', *xored)
        except Exception as e:
            raise errors.InterfaceError('Failed scrambling password; %s' % e)
        
        return hash4

    def _prepare_auth(self, usr, pwd, db, flags, seed):
        """Prepare elements of the authentication packet"""
        if usr is not None and len(usr) > 0:
            _username = usr.encode('utf-8') + b'\x00'
        else:
            _username = b'\x00'
        
        if pwd is not None and len(pwd) > 0:
            _password = utils.int1store(20) +\
                self._scramble_password(pwd.encode('utf-8'),seed)
        else:
            _password = b'\x00'
        
        if db is not None and len(db):
            _database = db.encode('utf-8') + b'\x00'
        else:
            _database = b'\x00'
        
        return (_username, _password, _database)

    def make_auth(self, seed, username=None, password=None, database=None,
                  charset=33, client_flags=0, max_allowed_packet=1073741824):
        """Make a MySQL Authentication packet"""
        if not seed:
            raise errors.ProgrammingError('Seed missing')

        auth = self._prepare_auth(username, password, database,
                                  client_flags, seed)
        data =  utils.int4store(client_flags) +\
                utils.int4store(max_allowed_packet) +\
                utils.int1store(charset) +\
                b'\x00' * 23 + auth[0] + auth[1] + auth[2]
        return data

    def make_auth_ssl(self, charset=33, client_flags=0,
                      max_allowed_packet=1073741824):
        """Make a SSL authentication packet"""
        return utils.int4store(client_flags) +\
               utils.int4store(max_allowed_packet) +\
               utils.int1store(charset) +\
               b'\x00' * 23
    
    def make_command(self, command, argument=None):
        """Make a MySQL packet containing a command"""
        data = utils.int1store(command)
        if argument is not None:
            data += argument
        return data
    
    def make_change_user(self, seed, username=None, password=None,
                         database=None, charset=33, client_flags=0):
        """Make a MySQL packet with the Change User command"""
        if not seed:
            raise errors.ProgrammingError('Seed missing')
        
        auth = self._prepare_auth(username, password, database,
                                  client_flags, seed)
        data = utils.int1store(ServerCmd.CHANGE_USER) +\
               auth[0] + auth[1] + auth[2] + utils.int2store(charset)
        return data
        
    def parse_handshake(self, packet):
        """Parse a MySQL Handshake-packet"""
        res = {}
        (packet, res['protocol']) = utils.read_int(packet[4:], 1)
        (packet, res['server_version_original']) = utils.read_string(
            packet, end=b'\x00')
        (packet, res['server_threadid']) = utils.read_int(packet, 4)
        (packet, res['scramble']) = utils.read_bytes(packet, 8)
        packet = packet[1:] # Filler 1 * \x00
        (packet, res['capabilities']) = utils.read_int(packet, 2)
        (packet, res['charset']) = utils.read_int(packet, 1)
        (packet, res['server_status']) = utils.read_int(packet, 2)
        packet = packet[13:] # Filler 13 * \x00
        (packet, scramble_next) = utils.read_bytes(packet, 12)
        res['scramble'] += scramble_next
        return res
        
    def parse_ok(self, packet):
        """Parse a MySQL OK-packet"""
        if not packet[4] == 0:
            raise errors.InterfaceError("Failed parsing OK packet.")

        ok = {}
        try:
            (packet, ok['field_count']) = utils.read_int(packet[4:], 1)
            (packet, ok['affected_rows']) = utils.read_lc_int(packet)
            (packet, ok['insert_id']) = utils.read_lc_int(packet)
            (packet, ok['server_status']) = utils.read_int(packet, 2)
            (packet, ok['warning_count']) = utils.read_int(packet, 2)
            if packet:
                (packet, ok['info_msg']) = utils.read_lc_string(packet)
                ok['info_msg'] = ok['info_msg'].decode('utf-8')
        except ValueError as err:
            raise errors.InterfaceError(
                "Failed parsing OK packet ({})".format(err))
        return ok
    
    def parse_column_count(self, packet):
        """Parse a MySQL packet with the number of columns in result set"""
        return utils.read_lc_int(packet[4:])[1]
        
    def parse_column(self, packet):
        """Parse a MySQL column-packet"""
        column = {}
        (packet, column['catalog']) = utils.read_lc_string(packet[4:])
        (packet, column['db']) = utils.read_lc_string(packet)
        (packet, column['table']) = utils.read_lc_string(packet)
        (packet, column['org_table']) = utils.read_lc_string(packet)
        (packet, column['name']) = utils.read_lc_string(packet)
        (packet, column['org_name']) = utils.read_lc_string(packet)
        packet = packet[1:] # filler 1 * \x00
        (packet, column['charset']) = utils.read_int(packet, 2)
        (packet, column['length']) = utils.read_int(packet,4)
        (packet, column['type']) = utils.read_int(packet, 1)
        (packet, column['flags']) = utils.read_int(packet, 2)
        (packet, column['decimal']) = utils.read_int(packet, 1)
        packet = packet[2:] # filler 2 * \x00
        
        return (
            column['name'].decode('utf-8'),
            column['type'],
            None, # display_size
            None, # internal_size
            None, # precision
            None, # scale
            ~column['flags'] & FieldFlag.NOT_NULL, # null_ok
            column['flags'], # MySQL specific
            )
        
    def parse_eof(self, packet):
        """Parse a MySQL EOF-packet"""
        res = {}
        packet = packet[1:] # disregard the first checking byte
        (packet, res['warning_count']) = utils.read_int(packet[4:], 2)
        (packet, res['status_flag']) = utils.read_int(packet, 2)
        return res

    def parse_statistics(self, packet):
        """Parse the statistics packet"""
        errmsg = "Failed getting COM_STATISTICS information"
        res = {}
         # Information is separated by 2 spaces
        pairs = packet[4:].split(b'\x20\x20')
        for pair in pairs:
            try:
                (lbl, val) = [ v.strip() for v in pair.split(b':', 2) ]
            except:
                raise errors.InterfaceError(errmsg)

            # It's either an integer or a decimal
            lbl = lbl.decode('utf-8')
            try:
                res[lbl] = int(val)
            except:
                try:
                    res[lbl] = Decimal(val.decode('utf-8'))
                except:
                    raise errors.InterfaceError(
                        "{} ({}:{}).".format(errmsg, lbl, val))
        return res

    def read_text_result(self, sock, count=1):
        """Read MySQL text result

        Reads all or given number of rows from the socket.

        Returns a tuple with 2 elements: a list with all rows and
        the EOF packet.
        """
        rows = []
        eof = None
        rowdata = None
        i = 0
        while True:
            if eof is not None:
                break
            if i == count:
                break
            packet = sock.recv()
            if packet[0:3] == b'\xff\xff\xff':
                data = packet[4:]
                packet = sock.recv()
                while packet[0:3] == b'\xff\xff\xff':
                    data += packet[4:]
                    packet = sock.recv()
                if packet[4] == 254:
                    eof = self.parse_eof(packet)
                else:
                    data += packet[4:]
                rowdata = utils.read_lc_string_list(data)
            elif packet[4] == 254:
                eof = self.parse_eof(packet)
                rowdata = None
            else:
                eof = None
                rowdata = utils.read_lc_string_list(packet[4:])
            if eof is None and rowdata is not None:
                rows.append(rowdata)
            i += 1
        return (rows, eof)
