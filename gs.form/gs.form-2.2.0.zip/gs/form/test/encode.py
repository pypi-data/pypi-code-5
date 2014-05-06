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
from cgi import FieldStorage
import os
try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python 3; forgive me.
    StringIO = None  # lint:ok
    from io import BytesIO
from unittest import TestCase, main as unittest_main
from gs.form.postmultipart import encode_multipart_formdata


class TestEncode(TestCase):
    '''Test the encode_content_type function of gs.form'''

    def setUp(self):
        self.fields = [('parrot', 'dead'), ('piranha', 'brother'),
                       ('ethyl', 'frog')]
        self.files = [('unwritten', 'rule.txt', 'This is a transgression.'),
                      ('boot', 'in.jpg', 'Tonight we look at violence.')]

    def test_encode_multipart_form_data_retval(self):
        '''Test that we get a 2-tuple back from the encode_multipart
        function'''
        retval = encode_multipart_formdata(self.fields, [])
        self.assertEqual(len(retval), 2)

    def test_encode_multipart_form_data_encoding(self):
        '''Test the function that encodes the data.'''
        contentType, data = encode_multipart_formdata(self.fields, [])
        self.assertEqual(contentType[:19], 'multipart/form-data')

    def test_encode_multipart_form_data_fields(self):
        '''Test the function that the field IDs are in the retval.'''
        contentType, data = encode_multipart_formdata(self.fields, [])
        names = ['name="{}"'.format(f[0]) for f in self.fields]
        for name in names:
            self.assertIn(name, data)

    def test_encode_multipart_form_data_files_names(self):
        '''Test the field-names for the files are right'''
        contentType, data = encode_multipart_formdata([], self.files)
        names = ['name="{}"'.format(f[0]) for f in self.files]
        for name in names:
            self.assertIn(name, data)

    def test_encode_multipart_form_data_files_filenames(self):
        '''Test the filenames for the files are right'''
        contentType, data = encode_multipart_formdata([], self.files)
        filenames = ['filename="{}"'.format(f[1]) for f in self.files]
        for filename in filenames:
            self.assertIn(filename, data)

    def test_parse(self):
        'Test if cgi.FieldStorage can parse the data'
        contentType, data = encode_multipart_formdata(self.fields, self.files)

        # --=mpj17=-- Marshall a data into an HTTP-like form, because it is
        # necesseary to pretend we does be a web server, weeee!
        # Replace newlines with carrage-return newlines because we does be a
        # webserver.
        bd = data.replace('\n', '\r\n')
        if StringIO:
            d = StringIO(bd)
        else:
            # Python 3 requires a bytes IO. Bless.
            d = BytesIO(bd.encode('utf-8'))
        # Set the environment variables, because we does be a webserver.
        # These are translated to "headers" by cgi.FieldStorage
        os.environ['CONTENT_TYPE'] = contentType  # < encode_multipart_formdata
        os.environ['REQUEST_METHOD'] = 'POST'
        # --=mpj17=-- Set the content length. An entire day was spent finding
        # out that if we omit doing this then the Python 3 cgi.FieldStorage
        # will have horrible pustular errors, with the wrong number of fields,
        # and the field names being totally out of wack. (It comes down to the
        # odd interaction with the cgi.FieldStorage.length and
        # cgi.FieldStorage.limit attributes.)
        os.environ['CONTENT_LENGTH'] = '{0}'.format(len(bd.encode('utf-8')))

        # Parse the data
        fs = FieldStorage(fp=d, environ=os.environ)

        # Test that we have the correct number of fields
        allFields = self.fields + self.files
        self.assertEqual(len(allFields), len(fs))

        # Test the normal fields have the correct IDs and values
        for fieldId, fieldValue in self.fields:
            self.assertIn(fieldId, fs)
            self.assertEqual(fieldId, fs[fieldId].name)
            self.assertEqual(fieldValue, fs[fieldId].value)

        # Test the files have the correct IDs, filenames, and values
        for fileId, filename, fileValue in self.files:
            self.assertIn(fileId, fs)
            self.assertEqual(fileId, fs[fileId].name)
            self.assertEqual(filename, fs[fileId].filename)
            self.assertEqual(fileValue, fs[fileId].value.decode('utf-8'))

if __name__ == '__main__':
    unittest_main()
