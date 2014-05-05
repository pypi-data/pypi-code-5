#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import re
import logging

LOG = logging.getLogger(__name__)

class FlipperProvider(object):

    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        from dbaas_credentials.credential import Credential
        from dbaas_credentials.models import CredentialType
        integration = CredentialType.objects.get(type= CredentialType.FLIPPER)

        return Credential.get_credentials(environment= environment, integration= integration)

    @classmethod
    def auth(self, environment):
        LOG.info("Conecting with flipper...")
        credentials = self.get_credentials(environment= environment)
        return MySQLdb.connect(host=credentials.endpoint, port=3306,
                                     user=credentials.user, passwd=credentials.password,
                                     db=credentials.project)
    

    @classmethod
    def create_flipper_dependencies(self, masterpairname, readip, writeip, instance1, instance2, environment):

        flipper_conn = self.auth(environment= environment)

        LOG.info("Flipper connection %s" % flipper_conn)
        flipper_cursor = flipper_conn.cursor()
        
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'broadcast', '10.25.12.255')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'mysql_password', 'flipit!')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'mysql_user', 'flipper')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'netmask', '255.255.255.0')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'quiesce_strategy', 'KillAll')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'read_ip', readip)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'send_arp_command', '/sbin/arping -I $sendarp_interface -c 5 -U -A $sendarp_ip')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'ssh_user', 'flipper')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'use_sudo', '1')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'write_ip', writeip)
        flipper_cursor.execute(sql_insert)
        
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'interface', 'eth2')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'ip', instance1.hostname.hostname)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'read_interface', 'eth2:98')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'write_interface', 'eth2:99')
        flipper_cursor.execute(sql_insert)

        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'interface', 'eth2')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'ip', instance2.hostname.hostname)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'read_interface', 'eth2:98')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'write_interface', 'eth2:99')
        flipper_cursor.execute(sql_insert)
        
        flipper_cursor.execute("commit")
    
    @classmethod
    def destroy_flipper_dependencies(self, name, environment):
        mp = (re.sub("[^a-zA-Z]","", name)[:20])

        flipper_conn = flipper_conn = self.auth(environment= environment)
        flipper_cursor = flipper_conn.cursor()
        
        sql_delete= "DELETE FROM masterpair  WHERE masterpair='%s' " % mp
        flipper_cursor.execute(sql_delete)

        sql_delete= "DELETE FROM node  WHERE masterpair='%s' " % mp
        flipper_cursor.execute(sql_delete)

        flipper_cursor.execute("commit")