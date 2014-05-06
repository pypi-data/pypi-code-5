# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from mock import MagicMock
import sys
if (sys.version_info < (3, )):
    from types import TupleType as tt
else:
    tt = tuple  # lint:ok
from unittest import TestCase
from gs.form.postmultipart import post_multipart, Connection
from gs.form.postmultipart import (HTTPSConnection as ph_HTTPSConnection,
    HTTPConnection as ph_HTTPConnection)
from gs.form.httplib import HTTPSConnection, HTTPConnection


class FauxResponse(tt):

    @property
    def status(self):
        return self[0]

    @property
    def reason(self):
        return self[1]

    def read(self):
        return self[2]


class TestPostMultipart(TestCase):
    '''Test the post_multipart function of gs.form'''
    fauxResponse = FauxResponse(('200', 'Mock',
                                 'He has joined the choir invisible'))
    fields = [('parrot', 'dead'), ('piranha', 'brother'),
              ('ethyl', 'frog')]
    files = [('unwritten', 'rule.txt', 'This is a transgression.'),
             ('toad', 'sprocket.jpg', 'Tonight we look at violence.')]

    def setUp(self):
        ph_HTTPConnection.getresponse = \
             MagicMock(return_value=self.fauxResponse)
        ph_HTTPConnection.request = MagicMock()

        ph_HTTPSConnection.getresponse = \
            MagicMock(return_value=self.fauxResponse)
        ph_HTTPSConnection.request = MagicMock()

    def test_connection(self):
        connection = Connection('example.com')
        self.assertIsInstance(connection.host, HTTPConnection)

    def test_connection_port_none(self):
        'Test the creation of a connection, when the netloc has no port'
        connection = Connection('example.com')
        self.assertEqual(connection.host.port, 80)

    def test_connection_port_odd(self):
        'Test the creation of a connection when the port in the netlock is odd'
        connection = Connection('example.com:1532')
        self.assertEqual(connection.host.port, 1532)

    def test_tls_connection(self):
        'Test the creation of a TLS (SSL) connection'
        tlsConnection = Connection('example.com', usessl=True)
        self.assertIsInstance(tlsConnection.host, HTTPSConnection)

    def test_post_multipart_resp(self):
        'Test that the response from post_mulitpart is the right length'
        r = post_multipart('example.com', 'form.html', self.fields)
        self.assertEqual(len(r), len(self.fauxResponse))

    def test_post_multipart_resp_status(self):
        'Test that the status from post_multipart is correct'
        r = post_multipart('example.com', 'form.html', self.fields)
        self.assertEqual(r[0], self.fauxResponse.status)

    def test_post_multipart_resp_reason(self):
        'Test that the "reason" from post_multipart is correct'
        r = post_multipart('example.com', 'form.html', self.fields)
        self.assertEqual(r[1], self.fauxResponse.reason)

    def test_post_multipart_resp_read(self):
        'Test that the data returned from post_multipart is correct'
        r = post_multipart('example.com', 'form.html', self.fields)
        self.assertEqual(r[2], self.fauxResponse.read())
