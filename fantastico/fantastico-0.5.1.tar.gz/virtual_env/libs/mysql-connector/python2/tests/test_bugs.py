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

"""Unittests for bugs
"""

import os
import sys
import gc
import tempfile
import logging
from datetime import datetime

import tests
from mysql.connector import (connection, cursor, conversion, protocol,
    utils, errors, constants)

logger = logging.getLogger(tests.LOGGER_NAME)

class Bug328998Tests(tests.MySQLConnectorTests):
    
    def test_set_connection_timetout(self):
        config = tests.MYSQL_CONFIG.copy()
        config['connection_timeout'] = 5
        self.db = connection.MySQLConnection(**config)
        self.assertEqual(config['connection_timeout'],
                         self.db._socket._connection_timeout)
        if self.db:
            self.db.disconnect()
    
    def test_timeout(self):
        config = tests.MYSQL_CONFIG.copy()
        config['connection_timeout'] = 1
        self.db = connection.MySQLConnection(**config)

        c = self.db.cursor()
        self.assertRaises(errors.InterfaceError,
            c.execute, "SELECT SLEEP(%d)" % (config['connection_timeout']+4))

        if self.db:
            self.db.disconnect()

class Bug437972Tests(tests.MySQLConnectorTests):

    def test_windows_tcp_connection(self):
        """lp:437972 TCP connection to Windows"""
        if os.name != 'nt':
            pass
        
        db = None
        try:
            db = connection.MySQLConnection(**tests.MYSQL_CONFIG)
        except errors.InterfaceError:
            self.fail()

        if db:
            db.close()

class Bug441430Tests(tests.MySQLConnectorTests):

    def test_execute_return(self):
        """lp:441430 cursor.execute*() should return the cursor.rowcount"""
        
        db = connection.MySQLConnection(**self.getMySQLConfig())
        c = db.cursor()
        tbl = "buglp44130"
        c.execute("DROP TABLE IF EXISTS %s" % tbl)
        c.execute("CREATE TABLE %s (id INT)" % tbl)
        c.execute("INSERT INTO %s VALUES (%%s),(%%s)" % tbl, (1,2,))
        self.assertEqual(2, c.rowcount)
        stmt = "INSERT INTO %s VALUES (%%s)" % tbl
        res = c.executemany(stmt,[(3,),(4,),(5,),(6,),(7,),(8,)])
        self.assertEqual(6, c.rowcount)
        res = c.execute("UPDATE %s SET id = id + %%s" % tbl , (10,))
        self.assertEqual(8, c.rowcount)
        c.close()
        db.close()
        
class Bug454782(tests.MySQLConnectorTests):
    
    def test_fetch_retun_values(self):
        """lp:454782 fetchone() does not follow pep-0249"""
        
        db = connection.MySQLConnection(**self.getMySQLConfig())
        c = db.cursor()
        self.assertEqual(None,c.fetchone())
        self.assertEqual([],c.fetchmany())
        self.assertRaises(errors.InterfaceError,c.fetchall)
        c.close()
        db.close()

class Bug454790(tests.MySQLConnectorTests):
    
    def test_pyformat(self):
        """lp:454790 pyformat / other named parameters broken"""
        
        db = connection.MySQLConnection(**self.getMySQLConfig())
        c = db.cursor()
        
        data = {'name': 'Geert','year':1977}
        c.execute("SELECT %(name)s,%(year)s", data)
        self.assertEqual((u'Geert',1977L),c.fetchone())
        
        data = [
            {'name': 'Geert', 'year': 1977},
            {'name': 'Marta', 'year': 1980}
            ]
        c.executemany("SELECT %(name)s,%(year)s", data)
        self.assertEqual(2, c.rowcount)
        c.close()
        db.close()

class Bug480360(tests.MySQLConnectorTests):
    
    def test_fetchall(self):
        """lp:480360: fetchall() should return [] when no result"""
        
        db = connection.MySQLConnection(**self.getMySQLConfig())
        c = db.cursor()
        
        # Trick to get empty result not needing any table
        c.execute("SELECT * FROM (SELECT 1) AS t WHERE 0 = 1")
        self.assertEqual([],c.fetchall())
        c.close()
        db.close()
        
class Bug380528(tests.MySQLConnectorTests):

    def test_old_password(self):
        """lp:380528: we do not support old passwords."""

        if tests.MYSQL_VERSION >= (5, 6, 6):
            # Test not valid for MySQL 5.6.6 and later.
            return

        config = self.getMySQLConfig()
        db = connection.MySQLConnection(**config)
        c = db.cursor()

        if config['unix_socket'] and os.name != 'nt':
            user = "'myconnpy'@'localhost'"
        else:
            user = "'myconnpy'@'%s'" % (config['host'])
        
        try:
            c.execute("GRANT SELECT ON %s.* TO %s" % (config['database'],user))
            c.execute("SET PASSWORD FOR %s = OLD_PASSWORD('fubar')" % (user))
        except:
            self.fail("Failed executing grant.")
        c.close()
        db.close()
        
        # Test using the newly created user
        test_config = config.copy()
        test_config['user'] = 'myconnpy'
        test_config['password'] = 'fubar'
        
        self.assertRaises(errors.NotSupportedError,
                          connection.MySQLConnection,**test_config)
            
        db = connection.MySQLConnection(**config)
        c = db.cursor()
        try:
            c.execute("REVOKE SELECT ON %s.* FROM %s" % (config['database'],user))
            c.execute("DROP USER %s" % (user))
        except:
            self.fail("Failed cleaning up user %s." % (user))
        c.close()
        db.close()

class Bug499362(tests.MySQLConnectorTests):
    
    def test_charset(self):
        """lp:499362 Setting character set at connection fails"""
        config = self.getMySQLConfig()
        config['charset'] = 'latin1'
        db = connection.MySQLConnection(**config)
        c = db.cursor()
        
        ver = db.get_server_version()
        if ver < (5,1,12):
            exp1 = [(u'character_set_client', u'latin1'), 
                (u'character_set_connection', u'latin1'),
                (u'character_set_database', u'utf8'),
                (u'character_set_filesystem', u'binary'),
                (u'character_set_results', u'latin1'),
                (u'character_set_server', u'utf8'),
                (u'character_set_system', u'utf8')]
            exp2 = [(u'character_set_client', u'latin2'),
                (u'character_set_connection', u'latin2'),
                (u'character_set_database', u'utf8'),
                (u'character_set_filesystem', u'binary'),
                (u'character_set_results', u'latin2'),
                (u'character_set_server', u'utf8'),
                (u'character_set_system', u'utf8')]
            varlst = []
            stmt = "SHOW SESSION VARIABLES LIKE 'character\_set\_%%'"
        else:
            exp1 = [(u'CHARACTER_SET_CONNECTION', u'latin1'),
                (u'CHARACTER_SET_CLIENT', u'latin1'),
                (u'CHARACTER_SET_RESULTS', u'latin1')]
            exp2 = [(u'CHARACTER_SET_CONNECTION', u'latin2'),
                (u'CHARACTER_SET_CLIENT', u'latin2'),
                (u'CHARACTER_SET_RESULTS', u'latin2')]
        
            varlst = ['character_set_client','character_set_connection',
                'character_set_results']
            stmt = """SELECT * FROM INFORMATION_SCHEMA.SESSION_VARIABLES
                WHERE VARIABLE_NAME IN (%s,%s,%s)"""
            
        c.execute(stmt, varlst)
        res1 = c.fetchall()
        db.set_charset_collation('latin2')
        c.execute(stmt, varlst)
        res2 = c.fetchall()
        
        c.close()
        db.close()
        
        self.assertTrue(self.cmpResult(exp1, res1))
        self.assertTrue(self.cmpResult(exp2, res2))

class Bug499410(tests.MySQLConnectorTests):
    
    def test_use_unicode(self):
        """lp:499410 Disabling unicode does not work"""
        config = self.getMySQLConfig()
        config['use_unicode'] = False
        db = connection.MySQLConnection(**config)
        
        self.assertEqual(False, db._use_unicode)
        db.close()
    
    def test_charset(self):
        config = self.getMySQLConfig()
        config['use_unicode'] = False
        charset = 'greek'
        config['charset'] = charset
        db = connection.MySQLConnection(**config)
        
        data = [
             # Bye in Greek
            '\xe1\xed\xf4\xdf\xef',
            ]
        
        exp_nonunicode = [(data[0],)]
        exp_unicode = [(u'\u03b1\u03bd\u03c4\u03af\u03bf',),]
        
        c = db.cursor()
        
        tbl = '%stest' % (charset)
        try:
            c.execute('DROP TABLE IF EXISTS %s' % (tbl))
            c.execute('CREATE TABLE %s (c1 VARCHAR(60)) charset=%s' %\
                (tbl,charset))
        except:
            self.fail("Failed creating test table.")
        
        try:
            stmt = 'INSERT INTO %s VALUES (%%s)' % (tbl)
            for line in data:
                c.execute(stmt, (line.strip(),))
        except:
            self.fail("Failed populating test table.")
        
        c.execute("SELECT * FROM %s" %(tbl))
        res_nonunicode = c.fetchall()
        db.set_unicode(True)
        c.execute("SELECT * FROM %s" %(tbl))
        res_unicode = c.fetchall()
        
        try:
            c.execute('DROP TABLE IF EXISTS %s' % (tbl))
        except:
            self.fail("Failed cleaning up test table.")
        
        db.close()
        
        self.assertEqual(exp_nonunicode,res_nonunicode)
        self.assertEqual(exp_unicode,res_unicode)

class Bug501290(tests.MySQLConnectorTests):
    """lp:501290 Client flags are set to None when connecting"""
    
    def setUp(self):
        config = self.getMySQLConfig()
        self.db = connection.MySQLConnection(**config)
    
    def tearDown(self):
        self.db.close()
    
    def test_default(self):
        """lp:501290 Check default client flags"""
        self.assertEqual(self.db._client_flags,
            constants.ClientFlag.get_default())
    
    def test_set_unset(self):
        """lp:501290 Set/unset one flag, check if set/unset"""
        orig = self.db._client_flags

        exp = constants.ClientFlag.get_default() | \
            constants.ClientFlag.COMPRESS    
        self.db.set_client_flags([constants.ClientFlag.COMPRESS])
        self.assertEqual(self.db._client_flags,exp)

        self.db.set_client_flags([-constants.ClientFlag.COMPRESS])
        self.assertEqual(self.db._client_flags, orig)
    
    def test_isset_client_flag(self):
        """lp:501290 Check if client flag is set"""
        data = constants.ClientFlag.get_default() | \
            constants.ClientFlag.COMPRESS
        
        self.db._client_flags = data
        self.assertEqual(True,
            self.db.isset_client_flag(constants.ClientFlag.COMPRESS))
    
class Bug507466(tests.MySQLConnectorTests):
    """lp:507466 BIT values are not converted correctly to Python"""
    
    def setUp(self):
        config = self.getMySQLConfig()
        self.db = connection.MySQLConnection(**config)
    
    def tearDown(self):
        try:
            c = self.db.cursor()
            c.execute("DROP TABLE IF EXISTS myconnpy_bits")
        except:
            pass
        self.db.close()
    
    def test_bits(self):
        """lp:507466 Store bitwise values in MySQL and retrieve them"""
        c = self.db.cursor()

        c.execute("DROP TABLE IF EXISTS myconnpy_bits")
        c.execute("""CREATE TABLE `myconnpy_bits` (
          `id` int NOT NULL AUTO_INCREMENT,
          `c1` bit(8) DEFAULT NULL,
          `c2` bit(16) DEFAULT NULL,
          `c3` bit(24) DEFAULT NULL,
          `c4` bit(32) DEFAULT NULL,
          `c5` bit(40) DEFAULT NULL,
          `c6` bit(48) DEFAULT NULL,
          `c7` bit(56) DEFAULT NULL,
          `c8` bit(64) DEFAULT NULL,
          PRIMARY KEY (id)
        )
        """)

        insert = """insert into myconnpy_bits (c1,c2,c3,c4,c5,c6,c7,c8)
            values (%s,%s,%s,%s,%s,%s,%s,%s)"""
        select = "SELECT c1,c2,c3,c4,c5,c6,c7,c8 FROM myconnpy_bits ORDER BY id"

        data = []
        data.append((0, 0, 0, 0, 0, 0, 0, 0))
        data.append((
            1 <<  7, 1 << 15, 1 << 23, 1 << 31,
            1 << 39, 1 << 47, 1 << 55, 1 << 63,
            ))
        c.executemany(insert, data)
        c.execute(select)
        rows = c.fetchall()
        
        self.assertEqual(rows, data)

class Bug510110(tests.MySQLConnectorTests):
    """lp:510110 Rollback fails when still reading"""
    
    def setUp(self):
        config = self.getMySQLConfig()
        self.db = connection.MySQLConnection(**config)
        self.c = self.db.cursor()
        
        self.tbl = 'Bug510110'
        self.c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        self.c.execute("""CREATE TABLE %s (
            id int unsigned auto_increment key,
            c1 varchar(20)
        ) ENGINE=InnoDB""" % (self.tbl))
    
    def tearDown(self):
        try:
            c = self.db.cursor()
            c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        except:
            pass
        self.db.close()
    
    def test_unbuffered(self):
        """lp:510110 InternalError exception with unbuffered cursor"""
        self.c.execute("INSERT INTO %s (c1) VALUES ('foo')" % (self.tbl))
        self.db.commit()
        self.c.execute("INSERT INTO %s (c1) VALUES ('bar')" % (self.tbl))
        self.c.execute("SELECT * FROM %s ORDER BY id" % (self.tbl))
        self.assertRaises(errors.InternalError,self.db.rollback)
    
    def test_buffered(self):
        """lp:510110 Buffered cursor, rollback is possible after SELECT"""
        self.c.close()
        self.db.buffered = True
        self.c = self.db.cursor()
        self.c.execute("INSERT INTO %s (c1) VALUES ('foo')" % (self.tbl))
        self.db.commit()
        self.c.execute("INSERT INTO %s (c1) VALUES ('bar')" % (self.tbl))
        self.db.rollback()
        self.c.execute("SELECT * FROM %s ORDER BY id" % (self.tbl))
        self.assertEqual([(1L, u'foo')],self.c.fetchall())

class Bug519301(tests.MySQLConnectorTests):
    """lp:519301 Temporary connection failures with 2 exceptions"""

    def test_auth(self):
        config = self.getMySQLConfig()
        config['user'] = 'ham'
        config['password'] = 'spam'
        db = None
        for i in xrange(1,100):
            try:
                db = connection.MySQLConnection(**config)
            except errors.ProgrammingError, e:
                pass
            except errors.Error, e:
                self.fail("Failing authenticating")
                break
            except:
                raise
            else:
                db.close()

class Bug524668(tests.MySQLConnectorTests):
    """lp:524668 Error in server handshake with latest code"""
    
    def test_handshake(self):
        """lp:524668 Error in server handshake with latest code"""
        
        handshake = '\x47\x00\x00\x00\x0a\x35\x2e\x30\x2e\x33\x30\x2d\x65'\
            '\x6e\x74\x65\x72\x70\x72\x69\x73\x65\x2d\x67\x70\x6c\x2d\x6c\x6f'\
            '\x67\x00\x09\x01\x00\x00\x68\x34\x69\x36\x6f\x50\x21\x4f\x00'\
            '\x2c\xa2\x08\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
            '\x00\x00\x4c\x6e\x67\x39\x26\x50\x44\x40\x57\x72\x59\x48\x00'
        
        p = protocol.MySQLProtocol()
        try:
            p.parse_handshake(handshake)
        except:
            raise
            self.fail("Failed handling handshake")

class Bug571201(tests.MySQLConnectorTests):
    """lp:571201 Problem with more than one statement at a time"""
    
    def setUp(self):
        config = self.getMySQLConfig()
        self.db = connection.MySQLConnection(**config)
        self.c = self.db.cursor()
        
        self.tbl = 'Bug571201'
        self.c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        self.c.execute("""CREATE TABLE %s (
            id INT AUTO_INCREMENT KEY,
            c1 INT
        )""" % (self.tbl))
    
    def tearDown(self):
        try:
            c = self.db.cursor()
            c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        except:
            pass
        self.db.close()
    
    def test_multistmts(self):
        """lp:571201 Problem with more than one statement at a time"""
        
        stmts = [
            "SELECT * FROM %s" % (self.tbl),
            "INSERT INTO %s (c1) VALUES (10),(20)" % (self.tbl),
            "SELECT * FROM %s" % (self.tbl),
            ]
        result_iter = self.c.execute(';'.join(stmts), multi=True)
        
        self.assertEqual(None, result_iter.next().fetchone())
        self.assertEqual(2, result_iter.next().rowcount)
        exp = [(1, 10), (2, 20)]
        self.assertEqual(exp, result_iter.next().fetchall())
        self.assertRaises(StopIteration, result_iter.next)

class Bug551533and586003(tests.MySQLConnectorTests):
    """lp: 551533, 586003: impossible to retrieve big result sets"""

    def setUp(self):
        config = self.getMySQLConfig()
        config['connection_timeout'] = 20
        self.db = connection.MySQLConnection(**config)
        self.c = self.db.cursor()

        self.tbl = 'Bug551533'
        self.c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        self.c.execute("""CREATE TABLE %s (
            id INT AUTO_INCREMENT KEY,
            c1 VARCHAR(100) DEFAULT 'abcabcabcabcabcabcabcabcabcabc'
        )""" % (self.tbl))

    def tearDown(self):
        try:
            c = self.db.cursor()
            c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        except:
            pass
        self.db.close()

    def test_select(self):
        """lp: 551533, 586003: impossible to retrieve big result sets"""

        insert = "INSERT INTO %s VALUES ()" % (self.tbl)
        exp = 20000
        i = exp
        while i > 0:
            self.c.execute(insert)
            i -= 1
        
        self.c.execute('SELECT * FROM %s LIMIT 20000' % (self.tbl))
        try:
            rows = self.c.fetchall()
        except Exception, e:
            self.fail("Failed retrieving big result set: %s" % e)
        else:
            self.assertEqual(exp, self.c.rowcount)

class Bug598706(tests.MySQLConnectorTests):
    """lp: 598706: config file in examples doesn't return the port"""

    def test_getport(self):
        """lp: 598706: config file in examples doesn't return the port"""
        
        from examples import config
        exp = 3306
        data = config.Config.dbinfo()
        self.assertEqual(exp, data['port'])

class Bug675425(tests.MySQLConnectorTests):
    """lp: 675425: Problems with apostrophe"""
    
    def setUp(self):
        config = self.getMySQLConfig()
        self.db = connection.MySQLConnection(**config)
        self.c = self.db.cursor()

        self.tbl = 'Bug551533'
        self.c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        self.c.execute("""CREATE TABLE %s (
            c1 VARCHAR(30),
            c2 VARCHAR(30)
        )""" % (self.tbl))

    def tearDown(self):
        try:
            c = self.db.cursor()
            c.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        except:
            pass
        self.db.close()
    
    def test_executemany_escape(self):
        """lp: 675425: Problems with apostrophe"""
        
        data = [("ham","spam",),("spam","ham",),
            ("ham \\' spam","spam ' ham",)]
        sql = "INSERT INTO %s VALUES (%%s,%%s)" % (self.tbl)
        try:
            self.c.executemany(sql, data)
        except:
            self.fail("Failed inserting using executemany"
                " and escaped strings")

class Bug695514(tests.MySQLConnectorTests):
    """lp: 695514: Infinite recursion when setting connection client_flags"""
    
    def test_client_flags(self):
        """lp: 695514: Infinite recursion when setting connection client_flags
        """
        try:
            config = self.getMySQLConfig()
            config['connection_timeout'] = 2
            config['client_flags'] = constants.ClientFlag.get_default()
            db = connection.MySQLConnection(**config)
            db.close()
        except:
            self.fail("Failed setting client_flags using integer")

class Bug809033(tests.MySQLConnectorTests):
    """lp: 809033: Lost connection causes infinite loop"""

    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cnx2 = connection.MySQLConnection(**config)
    
    def tearDown(self):
        try:
            self.cnx.close()
            self.cnx2.close()
        except:
            pass

    def test_lost_connection(self):
        """lp: 809033: Lost connection causes infinite loop"""
        if tests.WINDOWS_VERSION and tests.WINDOWS_VERSION_INFO < (6, 0):
            tests.MESSAGES['WARNINGS'].append(
                "Can't run tests for Bug809033 on Windows v%s" %\
                    tests.WINDOWS_VERSION)
            return
            return
        cur = self.cnx.cursor()
        cur2 = self.cnx2.cursor()

        cur.execute("SELECT REPEAT('a',1*1024*1024)")
        cur2.execute("KILL %d" % self.cnx.connection_id)
        self.assertRaises(errors.InterfaceError,cur.fetchone)

class Bug865859(tests.MySQLConnectorTests):
    """lp: 865859: sock.recv fails to return in some cases (infinite wait)"""

    def test_reassign_connection(self):
        """lp: 865859: sock.recv fails to return in some cases (infinite wait)
        """
        config = self.getMySQLConfig()
        config['connection_timeout'] = 1
        cnx = connection.MySQLConnection(**config)
        cur = cnx.cursor()
        cur.execute("DROP TABLE IF EXISTS t1")
        cur.execute("CREATE TABLE t1 (c1 INT)")
        cur.execute("INSERT INTO t1 (c1) VALUES (1)")

        try:
            cnx = connection.MySQLConnection(**config)
            cur = cnx.cursor()
            cur.execute("DROP TABLE IF EXISTS t1")
        except errors.InterfaceError, e:
            self.fail("Connection was not closed, we got timeout: %s" % e)

class BugOra13395083(tests.MySQLConnectorTests):
    def test_time_zone(self):
        """BUG#13395083: Using time zones"""
        config = self.getMySQLConfig()

        utc = tests.UTCTimeZone()
        testzone = tests.TestTimeZone(+2)

        # Store a datetime in UTC into a TIMESTAMP column
        config['time_zone'] = "+00:00"
        now_utc = datetime.utcnow().replace(microsecond=0,tzinfo=utc)

        cnx = connection.MySQLConnection(**config)
        cur = cnx.cursor()
        cur.execute("DROP TABLE IF EXISTS t1")
        cur.execute("CREATE TABLE t1 (c1 TIMESTAMP)")
        cur.execute("INSERT INTO t1 (c1) VALUES (%s)", (now_utc,))
        cnx.commit()

        cur.execute("SELECT c1 FROM t1")
        row = cur.fetchone()
        self.assertEqual(now_utc,row[0].replace(tzinfo=utc))

        cnx.set_time_zone("+02:00")
        cur.execute("SELECT c1 FROM t1")
        row = cur.fetchone()
        self.assertEqual(now_utc.astimezone(testzone),
            row[0].replace(tzinfo=testzone))

        cnx.close()

class BugOra13392739(tests.MySQLConnectorTests):
    def test_ping(self):
        """BUG#13392739: MySQLConnection.ping()"""
        config = self.getMySQLConfig()
        config['connection_timeout'] = 2
        config['unix_socket'] = None

        cnx = connection.MySQLConnection()
        self.assertRaises(errors.InterfaceError,cnx.ping)

        cnx = connection.MySQLConnection(**config)
        try:
            cnx.ping()
        except Exception, e:
            self.fail("Error raised although connection should be "
                "available (%s)." % e)
        
        cnx.disconnect()
        self.assertRaises(errors.InterfaceError,cnx.ping)

        try:
            cnx.ping(reconnect=True)
        except Exception, e:
            self.fail("Error raised although ping should reconnect. (%s)" % e)
        
        # Temper with the host to which we reconnect to simulate the
        # MySQL not being available.
        cnx.disconnect()
        cnx._host = 'some-unknown-host-somwhere-on.mars'
        self.assertRaises(errors.InterfaceError, cnx.ping, reconnect=True)

    def test_reconnect(self):
        """BUG#13392739: MySQLConnection.reconnect()"""
        config = self.getMySQLConfig()
        config['connection_timeout'] = 1
        config['unix_socket'] = None

        cnx = connection.MySQLConnection(**config)
        cnx.disconnect()
        self.assertRaises(errors.InterfaceError,cnx.ping)
        try:
            cnx.reconnect()
        except:
            self.fail("Errors raised although connection should have been "
                "reconnected.")
        
        cnx.disconnect()
        # Temper with the host to which we reconnect to simulate the
        # MySQL not being available.
        cnx._host = 'some-unknown-host-somwhere-on.mars'
        self.assertRaises(errors.InterfaceError,cnx.reconnect)
        try:
            cnx.reconnect(attempts=3)
        except errors.InterfaceError, e:
            self.assertTrue('3 attempt(s)' in str(e))

class BugOra13435186(tests.MySQLConnectorTests):
    def setUp(self):
        self.sample_size = 4
        self._reset_samples()
        gc.collect()
    
    def _reset_samples(self):
        self.samples = [0,] * self.sample_size
    
    def _assert_flat_line(self, samples):
        for i in range(0, len(samples)-1):
            try:
                if samples[i] != samples[i+1]:
                    self.fail("No flat-line for number of collected objects")
            except IndexError:
                pass # We are at the end.
    
    def test_converter(self):
        for i in range(0, self.sample_size):
            conv = conversion.MySQLConverter()
            self.samples[i] = len(gc.get_objects())
        
        self._assert_flat_line(self.samples)
    
    def test_connection(self):
        config = self.getMySQLConfig()
        
        # Create a connection and close using close()-method
        for i in range(0, self.sample_size):
            cnx = connection.MySQLConnection(**config)
            cnx.close()
            self.samples[i] = len(gc.get_objects())
        
        self._assert_flat_line(self.samples)
        
        self._reset_samples()
        # Create a connection and rely on destructor to close
        for i in range(0, self.sample_size):
            cnx = connection.MySQLConnection(**config)
            self.samples[i] = len(gc.get_objects())
        
        self._assert_flat_line(self.samples)

    def test_cursor(self):
        config = self.getMySQLConfig()
        cnx = connection.MySQLConnection(**config)
        
        # Create a cursor and close using close()-method
        for i in range(0, self.sample_size):
            cursor = cnx.cursor()
            cursor.close()
            self.samples[i] = len(gc.get_objects())
        
        self._assert_flat_line(self.samples)
        
        self._reset_samples()
        # Create a cursor and rely on destructor to close
        for i in range(0, self.sample_size):
            cursor = cnx.cursor()
            self.samples[i] = len(gc.get_objects())
        
        self._assert_flat_line(self.samples)

class BugOra14184643(tests.MySQLConnectorTests):
    """BUG#14184643: cmd_query() disregards waiting results"""
    def setUp(self):
        config = self.getMySQLConfig()
        config['connection_timeout'] = 5
        self.cnx = connection.MySQLConnection(**config)
        
    def test_cmd_query(self):
        """BUG#14184643: cmd_query()"""
        
        self.cnx.cmd_query('SELECT 1')
        self.assertRaises(errors.InternalError, self.cnx.cmd_query,
                          'SELECT 2')
    
    def test_get_rows(self):
        """BUG#14184643: get_row() and get_rows()"""
        self.cnx.cmd_query('SELECT 1')
        self.cnx.get_rows()
        self.assertRaises(errors.InternalError, self.cnx.get_rows)
        
        self.cnx.cmd_query('SELECT 1')
        self.cnx.get_row()
        self.assertEqual(None, self.cnx.get_row()[0])
        self.assertRaises(errors.InternalError, self.cnx.get_row)

    def test_cmd_statistics(self):
        """BUG#14184643: other command after cmd_query()"""
        self.cnx.cmd_query('SELECT 1')
        self.assertRaises(errors.InternalError, self.cnx.cmd_statistics)
        self.cnx.get_rows()

class BugOra14208326(tests.MySQLConnectorTests):
    """BUG#14208326: cmd_query() does not handle multiple statements"""
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cursor = self.cnx.cursor()
        
        self.table = "BugOra14208326"
        self.cnx.cmd_query("DROP TABLE IF EXISTS %s" % self.table)
        self.cnx.cmd_query("CREATE TABLE %s (id INT)" % self.table)
    
    def test_cmd_query(self):
        """BUG#14208326: cmd_query() should not allow multiple results"""
        self.assertRaises(errors.InterfaceError,
                          self.cnx.cmd_query, 'SELECT 1; SELECT 2')
    
    def test_cmd_query_iter(self):
        stmt = 'SELECT 1; INSERT INTO %s VALUES (1),(2); SELECT 3'
        results = []
        for result in self.cnx.cmd_query_iter(stmt % self.table):
            results.append(result)
            if 'columns' in result:
                results.append(self.cnx.get_rows())

class BugOra14201459(tests.MySQLConnectorTests):
    """BUG#14201459: Server error 1426 should raise ProgrammingError"""
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cursor = self.cnx.cursor()
        
        self.tbl = 'Bug14201459'
        self.cursor.execute("DROP TABLE IF EXISTS %s" % (self.tbl))

    def test_error1426(self):
        create = "CREATE TABLE %s (c1 TIME(7))" % self.tbl
        try:
            self.cursor.execute(create)
        except errors.ProgrammingError, exception:
            if tests.MYSQL_VERSION < (5, 6, 4) and exception.errno != 1064:
                self.fail("ProgrammingError is not Error 1064")
            elif tests.MYSQL_VERSION >= (5, 6, 4) and exception.errno != 1426:
                self.fail("ProgrammingError is not Error 1426")
        else:
            self.fail("ProgrammingError not raised")

class BugOra14231160(tests.MySQLConnectorTests):
    """BUG#14231160: lastrowid, description and rowcount read-only"""
    def test_readonly_properties(self):
        cur = cursor.MySQLCursor()
        for attr in ('description', 'rowcount', 'lastrowid'):
            try:
                setattr(cur, attr, 'spam')
            except AttributeError, err:
                # It's readonly, that's OK
                pass
            else:
                self.fail('Need read-only property: %s' % attr)

class BugOra14259954(tests.MySQLConnectorTests):
    """BUG#14259954: ON DUPLICATE KEY UPDATE VALUE FAILS REGEX"""
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cursor = self.cnx.cursor()
        
        self.tbl = 'Bug14259954'
        self.cursor.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        create = ("CREATE TABLE %s ( "
                  "`id` int(11) NOT NULL AUTO_INCREMENT, "
                  "`c1` int(11) NOT NULL DEFAULT '0', "
                  "PRIMARY KEY (`id`,`c1`))" % (self.tbl))
        self.cursor.execute(create)

    def test_executemany(self):
        query = ("INSERT INTO %s (id,c1) VALUES (%%s,%%s) "
                 "ON DUPLICATE KEY UPDATE c1=VALUES(c1)") % self.tbl
        try:
            self.cursor.executemany(query, [(1,1),(2,2)])
        except errors.ProgrammingError, err:
            self.fail("Regular expression fails with executemany(): %s" %
                      err)


class BugOra14548043(tests.MySQLConnectorTests):
    """BUG#14548043: ERROR MESSAGE SHOULD BE IMPROVED TO DIAGNOSE THE PROBLEM
    """
    def test_unix_socket(self):
        config = self.getMySQLConfig()
        config['unix_socket'] = os.path.join(
            tempfile.gettempdir(), 'a'*100 + 'myconnpy_bug14548043.test')

        exp = ("2002: Can't connect to local MySQL "
            "server through socket '%s' "
            "(AF_UNIX path too long)" % config['unix_socket'][0:100])

        try:
            cnx = connection.MySQLConnection(**config)
        except errors.InterfaceError, err:
            self.assertEqual(exp, str(err))

class BugOra14754894(tests.MySQLConnectorTests):
    """
    """
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cursor = self.cnx.cursor()

        self.tbl = 'BugOra14754894'
        self.cursor.execute("DROP TABLE IF EXISTS %s" % (self.tbl))
        self.cursor.execute("CREATE TABLE %s (c1 INT)" % (self.tbl))

    def test_executemany(self):
        insert = "INSERT INTO %s (c1) VALUES (%%(c1)s)" % (self.tbl)
        data = [{'c1': 1}]
        self.cursor.executemany(insert, [{'c1': 1}])

        try:
            self.cursor.executemany(insert, [{'c1': 1}])
        except ValueError, err:
            self.fail(err)

        self.cursor.execute("SELECT c1 FROM %s" % self.tbl)
        self.assertEqual(data[0]['c1'], self.cursor.fetchone()[0])

class BugOra14843456(tests.MySQLConnectorTests):
    """BUG#14843456: UNICODE USERNAME AND/OR PASSWORD FAILS
    """
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cursor = self.cnx.cursor()

        if config['unix_socket'] and os.name != 'nt':
            host = 'localhost'
        else:
            host = config['host']

        grant = (u"CREATE USER '%s'@'%s' "
                 u"IDENTIFIED BY '%s'")

        self._credentials = [
            (u'Herne', u'Herne'),
            (u'\u0141owicz', u'\u0141owicz'),
            ]
        for user, password in self._credentials:
            self.cursor.execute(grant % (user, host, password))

    def test_unicode_credentials(self):
        config = self.getMySQLConfig()
        for user, password in self._credentials:
            config['user'] = user
            config['password'] = password
            config['database'] = None
            try:
                cnx = connection.MySQLConnection(**config)
            except (UnicodeDecodeError, errors.InterfaceError):
                self.fail('Failed using unicode username or password')

class BugOra13808727(tests.MySQLConnectorTests):
    """BUG#13808727: ERROR UNCLEAR WHEN TCP PORT IS NOT AN INTEGER
    """
    def test_portnumber(self):
        config = self.getMySQLConfig()
        try:
            config['port'] = str(config['port'])
            connection.MySQLConnection(**config)
        except:
            self.fail("Port number as string is not accepted.")

        self.assertRaises(errors.InterfaceError,
                          connection.MySQLConnection, port="spam")

class BugOra15876886(tests.MySQLConnectorTests):
    """BUG#15876886: CONNECTOR/PYTHON CAN NOT CONNECT TO MYSQL THROUGH IPV6
    """
    def test_ipv6(self):
        if not tests.IPV6_AVAILABLE:
            tests.MESSAGES['WARNINGS'].append(
                           "Could not test IPv6. Use options "
                           "--bind-address=:: --host=::1 and"
                           " make sure the OS and Python supports IPv6.")
            return

        config = self.getMySQLConfig()
        config['host'] = '::1'
        config['unix_socket'] = None
        try:
            cnx = connection.MySQLConnection(**config)
        except errors.InterfaceError:
            self.fail("Can not connect using IPv6")

class BugOra15915243(tests.MySQLConnectorTests):
    """BUG#15915243: PING COMMAND ALWAYS RECONNECTS TO THE DATABASE
    """
    def test_ping(self):
        config = self.getMySQLConfig()

        cnx = connection.MySQLConnection(**config)
        cid = cnx.connection_id
        cnx.ping()
        # Do not reconnect
        self.assertEqual(cid, cnx.connection_id)
        cnx.close()
        # Do not reconnect
        self.assertRaises(errors.InterfaceError, cnx.ping)
        # Do reconnect
        cnx.ping(reconnect=True)
        self.assertNotEqual(cid, cnx.connection_id)
        cnx.close()

class BugOra15916486(tests.MySQLConnectorTests):
    """BUG#15916486: RESULTS AFTER STORED PROCEDURE WITH ARGUMENTS ARE NOT KEPT
    """
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)
        self.cur = self.cnx.cursor()

        self.cur.execute("DROP PROCEDURE IF EXISTS sp1")
        self.cur.execute("DROP PROCEDURE IF EXISTS sp2")
        sp1 = ("CREATE PROCEDURE sp1(IN pIn INT, OUT pOut INT)"
               " BEGIN SELECT 1; SET pOut := pIn; SELECT 2; END")
        sp2 = ("CREATE PROCEDURE sp2 ()"
               " BEGIN SELECT 1; SELECT 2; END")

        self.cur.execute(sp1)
        self.cur.execute(sp2)

    def tearDown(self):
        try:
            self.cur.execute("DROP PROCEDURE IF EXISTS sp1")
            self.cur.execute("DROP PROCEDURE IF EXISTS sp2")
        except:
            pass # Clean up fail is acceptable for this test

        self.cnx.close()

    def test_callproc_with_args(self):
        exp = (5, 5)
        self.assertEqual(exp, self.cur.callproc('sp1', (5, 0)))

        exp = [[(1,)], [(2,)]]
        results = []
        for result in self.cur.stored_results():
            results.append(result.fetchall())
        self.assertEqual(exp, results)

    def test_callproc_without_args(self):
        exp = ()
        self.assertEqual(exp, self.cur.callproc('sp2'))

        exp = [[(1,)], [(2,)]]
        results = []
        for result in self.cur.stored_results():
            results.append(result.fetchall())
        self.assertEqual(exp, results)

class BugOra15836979(tests.MySQLConnectorTests):
    """BUG#15836979: UNCLEAR ERROR MESSAGE CONNECTING USING UNALLOWED IP ADDRESS
    """
    def setUp(self):
        if os.name == 'nt':
            return
        config = self.getMySQLConfig()
        cnx = connection.MySQLConnection(**config)
        cnx.cmd_query("DROP USER 'root'@'127.0.0.1'")
        try:
            cnx.cmd_query("DROP USER 'root'@'::1'")
        except errors.DatabaseError:
            # Some MySQL servers have no IPv6 entry
            pass
        cnx.close()

    def tearDown(self):
        if os.name == 'nt':
            return
        config = self.getMySQLConfig()
        cnx = connection.MySQLConnection(**config)
        cnx.cmd_query(
            "GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' "
            "WITH GRANT OPTION")
        cnx.cmd_query(
            "GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1' "
            "WITH GRANT OPTION")
        cnx.close()

    def test_handshake(self):
        if os.name == 'nt':
            tests.MESSAGES['WARNINGS'].append(
                "Can't test error handling when doing handshake "
                "on Windows (lacking named pipe support)")
            return
        config = self.getMySQLConfig()
        config['host'] = '127.0.0.1'
        config['unix_socket'] = None
        self.assertRaises(errors.DatabaseError,
                          connection.MySQLConnection, **config)

class BugOra16217743(tests.MySQLConnectorTests):
    """BUG#16217743: CALLPROC FUNCTION WITH STRING PARAMETERS
    """
    def setUp(self):
        config = self.getMySQLConfig()
        self.cnx = connection.MySQLConnection(**config)

        self.cnx.cmd_query("DROP TABLE IF EXISTS bug16217743")
        self.cnx.cmd_query("DROP PROCEDURE IF EXISTS sp_bug16217743")
        self.cnx.cmd_query("CREATE TABLE bug16217743 (c1 VARCHAR(20), c2 INT)")
        self.cnx.cmd_query(
            "CREATE PROCEDURE sp_bug16217743 (p1 VARCHAR(20), p2 INT) "
            "BEGIN INSERT INTO bug16217743 (c1, c2) "
            "VALUES (p1, p2); END;")

    def tearDown(self):
        self.cnx.cmd_query("DROP TABLE IF EXISTS bug16217743")
        self.cnx.cmd_query("DROP PROCEDURE IF EXISTS sp_bug16217743")

    def test_procedure(self):
        exp = (u'ham', 42)
        cur = self.cnx.cursor()
        cur.callproc('sp_bug16217743', ('ham', 42))
        cur.execute("SELECT c1, c2 FROM bug16217743")
        self.assertEqual(exp, cur.fetchone())


class BugOra16217667(tests.MySQLConnectorTests):
    """BUG#16217667: PYTHON CONNECTOR 3.2 SSL CONNECTION FAILS
    """
    def setUp(self):
        config = self.getMySQLConfig()
        self.admin_cnx = connection.MySQLConnection(**config)

        self.admin_cnx.cmd_query(
            "GRANT ALL ON %s.* TO 'ssluser'@'%s' REQUIRE X509" % (
                config['database'], tests.MYSQL_CONFIG['host']))

    def tearDown(self):
        self.admin_cnx.cmd_query("DROP USER 'ssluser'@'%s'" % (
            tests.MYSQL_CONFIG['host']))

    def test_sslauth(self):
        if not tests.SSL_AVAILABLE:
            tests.MESSAGES['WARNINGS'].append(
                "BugOra16217667 test failed. Python lacks SSL support.")
            return

        config = self.getMySQLConfig()
        config['user'] = 'ssluser'
        config['password'] = ''
        config['unix_socket'] = None
        config['ssl_verify_cert'] = True
        config.update({
            'ssl_ca': os.path.abspath(
                os.path.join(tests.SSL_DIR, 'tests_CA_cert.pem')),
            'ssl_cert': os.path.abspath(
                os.path.join(tests.SSL_DIR, 'tests_client_cert.pem')),
            'ssl_key': os.path.abspath(
                os.path.join(tests.SSL_DIR, 'tests_client_key.pem')),
        })

        try:
            cnx = connection.MySQLConnection(**config)
        except errors.ProgrammingError:
            self.fail("Failed authentication with SSL")

        cnx.cmd_query("SHOW STATUS LIKE 'Ssl_cipher'")
        self.assertTrue(cnx.get_rows()[0][0] != u'')


class BugOra16316049(tests.MySQLConnectorTests):
    """ SSL ERROR: [SSL: TLSV1_ALERT_UNKNOWN_CA] AFTER FIX 6217667"""
    def setUp(self):
        config = self.getMySQLConfig()
        self.admin_cnx = connection.MySQLConnection(**config)

        self.admin_cnx.cmd_query(
            "GRANT ALL ON %s.* TO 'ssluser'@'%s' REQUIRE SSL" % (
                config['database'], tests.MYSQL_CONFIG['host']))

    def tearDown(self):
        self.admin_cnx.cmd_query("DROP USER 'ssluser'@'%s'" % (
            tests.MYSQL_CONFIG['host']))

    def test_ssl(self):
        if not tests.SSL_AVAILABLE:
            tests.MESSAGES['WARNINGS'].append(
                "BugOra16217667 test failed. Python lacks SSL support.")
            return

        ssl_ca = os.path.abspath(
            os.path.join(tests.SSL_DIR, 'tests_CA_cert.pem'))
        ssl_cert = os.path.abspath(
            os.path.join(tests.SSL_DIR, 'tests_client_cert.pem'))
        ssl_key = os.path.abspath(
            os.path.join(tests.SSL_DIR, 'tests_client_key.pem'))

        config = self.getMySQLConfig()
        config['user'] = 'ssluser'
        config['password'] = ''
        config['unix_socket'] = None
        config.update({
            'ssl_ca': None,
            'ssl_cert': None,
            'ssl_key': None,
        })

        # User requires SSL, but no values for ssl argument given
        self.assertRaises(errors.ProgrammingError,
                          connection.MySQLConnection, **config)

        # Use wrong value for ssl_ca
        config['ssl_ca'] = os.path.abspath(
            os.path.join(tests.SSL_DIR, 'tests_ca_cert.pem'))
        config['ssl_cert'] = ssl_cert
        config['ssl_key'] = ssl_key
        config['ssl_verify_cert'] = True
        self.assertRaises(errors.InterfaceError,
                          connection.MySQLConnection, **config)

        # Use correct value
        config['ssl_ca'] = ssl_ca
        try:
            cnx = connection.MySQLConnection(**config)
        except errors.ProgrammingError:
            self.fail("Failed authentication with SSL")

        cnx.cmd_query("SHOW STATUS LIKE 'Ssl_cipher'")
        self.assertTrue(cnx.get_rows()[0][0] != u'')


class BugOra16369511(tests.MySQLConnectorTests):
    """BUG#16369511: LOAD DATA LOCAL INFILE IS MISSING
    """
    def setUp(self):
        config = self.getMySQLConfig()
        config['client_flags'] = [constants.ClientFlag.LOCAL_FILES]
        self.cnx = connection.MySQLConnection(**config)
        self.cur = self.cnx.cursor()

        self.data_file = os.path.join(
            'python%s' % sys.version_info[0],
            'tests', 'data', 'local_data.csv')

        self.cur.execute("DROP TABLE IF EXISTS local_data")
        self.cur.execute(
            "CREATE TABLE local_data (id int, c1 VARCHAR(6), c2 VARCHAR(6))")

    def tearDown(self):
        self.cur.execute("DROP TABLE IF EXISTS local_data")

    def test_load_csv(self):
        sql = "LOAD DATA LOCAL INFILE %s INTO TABLE local_data"
        self.cur.execute(sql, (self.data_file,))
        self.cur.execute("SELECT * FROM local_data")

        exp = [
            (1, u'c1_1', u'c2_1'), (2, u'c1_2', u'c2_2'),
            (3, u'c1_3', u'c2_3'), (4, u'c1_4', u'c2_4'),
            (5, u'c1_5', u'c2_5'), (6, u'c1_6', u'c2_6')]
        self.assertEqual(exp, self.cur.fetchall())

    def test_filenotfound(self):
        sql = "LOAD DATA LOCAL INFILE %s INTO TABLE local_data"
        self.assertRaises(errors.InterfaceError,
                          self.cur.execute, sql, (self.data_file + '_spam',))

