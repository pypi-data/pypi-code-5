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
from unittest import TestCase
from gs.form.postmultipart import get_content_type


class TestContentType(TestCase):
    '''Test the content-type guesser component of gs.form'''

    def content_type_test(self, filename, expectedType):
        '''Test that a file name is of an expected type'''
        ct = get_content_type(filename)
        self.assertEqual(ct, expectedType)

    def test_get_content_type_txt(self):
        '''Test the function that guesses the content type of a text file.'''
        self.content_type_test('foo.txt', 'text/plain')

    def test_get_content_type_jpg(self):
        '''Test the function that guesses the content type of a JPEG file.'''
        self.content_type_test('foo.jpg', 'image/jpeg')

    def test_get_content_type_mpg(self):
        '''Test the function that guesses the content type of a MPEG file.'''
        self.content_type_test('foo.mpg', 'video/mpeg')

    def test_get_content_type_bar(self):
        '''Test the function that guesses the content type of a odd file.'''
        self.content_type_test('foo.bar', 'application/octet-stream')
