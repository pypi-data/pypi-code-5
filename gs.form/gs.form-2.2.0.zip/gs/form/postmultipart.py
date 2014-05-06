# -*- coding: utf-8 -*-
'POST data to a a page.'
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
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.header import Header
import mimetypes
from gs.core import to_unicode_or_bust
from .httplib import HTTPSConnection, HTTPConnection
UTF8 = 'utf-8'


class Connection(object):
    '''A wrapper for the HTTP(S) connection'''
    def __init__(self, netloc, usessl=False):
        '''Initalise the connection

:param str netloc: The netloc (``host`` or ``host:port``).
:param bool usessl: ``True`` if TLS should be used.
'''
        if usessl:
            self.connectionFactory = HTTPSConnection
        else:
            self.connectionFactory = HTTPConnection
        self.host = self.connectionFactory(netloc)

    def request(self, requestType, selector, body, headers):
        '''Make a request. Wraps :meth:`http.client.HTTPConnection.request`.'''
        self.host.request(requestType, selector, body, headers)

    def getresponse(self):
        '''Make a  response.
        Wraps :meth:`http.client.HTTPConnection.getresponse`.'''
        retval = self.host.getresponse()
        return retval


def post_multipart(netloc, selector, fields, files=[], usessl=False):
    """Post fields and files to an http host as ``multipart/form-data``.

:param str netloc: The netloc (``host`` or ``host:port``).
:param str selector: The path to the form that will be posted to.
:param list fields: A sequence of ``(name, value)`` 2-tuple elements for
                    regular form fields.
:param list files: A sequence of ``(name, filename, value)`` 3-tuple elements
                   for data to be uploaded as files
:param bool usessl: ``True`` if TLS should be used to communicate with the
                    server.
:return: A 3-tuple: the reponse-status, reason, and data.

**Example**:

    Post three normal form fields (``parrot``, ``piranah``, and ``ethyl``) and
    one file (the text file ``rule.txt``, sent as the ``unwritten`` form field)
    to ``example.com`` on port ``2585``, using normal HTTP rather than TLS
    (the default)::

        fields = [('parrot', 'dead'), ('piranha', 'brother'),
                  ('ethyl', 'frog')]
        files = [('unwritten', 'rule.txt', 'This is a transgression.')]
        r = post_multipart('example.com:2585', '/form.html', fields, files)
        status, reason, data = r
"""
    if type(fields) == dict:
        f = list(fields.items())
    else:
        f = fields
    #if type(f) not in (list, tuple):
    #    m = 'Fields must be a dict, tuple, or list, not "{0}".'
    #    msg = m.format(type(fields))
    #    raise ValueError(msg)

    connection = Connection(netloc, usessl=usessl)
    content_type, body = encode_multipart_formdata(f, files)
    headers = {
        'User-Agent': 'gs.form',
        'Content-Type': content_type
        }

    connection.request('POST', selector, body, headers)
    res = connection.getresponse()
    return res.status, res.reason, res.read()


def encode_multipart_formdata(fields, files):
    """Encode the data into a multipart-document

    :param list fields: A  sequence of ``(name, value)`` 2-tuple elements,
                        for regular form fields.
    :param list files: A sequence of ``(name, filename, value)`` 3-tuple
                       elements for data to be uploaded as files
    :return: ``(content_type, body)`` as a 2-tuple ready to be sent in a POST.
    :rtype: ``tuple``
"""
    container = MIMEMultipart('form-data')
    for (key, value) in fields:
        part = MIMENonMultipart('foo', 'bar')
        part['Content-Disposition'] = Header('form-data').encode()
        part.set_param('name', key, 'Content-Disposition')
        data = to_unicode_or_bust(value).encode(UTF8)
        part.set_payload(data)
        del(part['Content-Type'])
        del(part['MIME-Version'])
        container.attach(part)
    for (key, filename, value) in files:
        part = MIMENonMultipart('foo', 'bar')
        part['Content-Disposition'] = Header('form-data').encode()
        part.set_param('name', key, 'Content-Disposition')
        part.set_param('filename', filename, 'Content-Disposition')
        part['Content-Type'] = Header(get_content_type(filename)).encode()
        part.set_payload(value)
        del(part['Content-Type'])
        del(part['MIME-Version'])
        container.attach(part)

    # Drop the MIME-version header. Useless in forms
    del(container['MIME-Version'])
    # Put the Content-type header on one line
    buf = container.as_string()
    # Grab the Content-type header
    splitBuf = buf.replace('\n', '', 1).strip().split('\n')
    content_type = splitBuf[0].split(': ')[1]
    # Drop the content-type header from the data
    rbuf = '\n'.join(splitBuf[1:]).strip() + '\n\n'
    return content_type, rbuf


def get_content_type(filename):
    '''Get the content type of a file

    :param str filename: The name of the file.
    :return: The MIME-type of the file, or ``application/octet-stream``.
    :rtype: ``str``'''
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
