# -*- coding: utf-8 -*-
#    Asymmetric Base Framework :: Fields
#    Copyright (C) 2013-2014  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.utils import unittest

from asymm_fields.fields.quantityfield import ZERO_QTY

from .testapp.models import CommentModel, IntegerRangeModel, LongMessageModel, LongNameModel, \
	QtyModel, ShortMessageModel, ShortNameModel, UUIDModel


class Test(unittest.TestCase):
	
	def setUp(self):
		loading.cache.loaded = False
		migrate = 'south' not in settings.INSTALLED_APPS
		call_command('syncdb', verbosity = 0, migrate = migrate)
	
	def test_comment_model(self):
		# Shouldn't error
		m = CommentModel(field1 = "*" * 1024)
		m.save()
	
	def test_integer_model(self):
		# Shouldn't error
		m = IntegerRangeModel(field1 = 1)
		m.save()
	
	def test_long_message(self):
		# Shouldn't error
		m = LongMessageModel(field1 = '*' * 255)
		m.save()
	
	def test_long_name(self):
		m = LongNameModel(field1 = '*' * 285)
		m.save()
	
	def test_qty(self):
		m = QtyModel()
		m.save()
		
		m2 = QtyModel.objects.get(pk = m.id)
		self.assertEqual(m2.field1, ZERO_QTY)
		
		m = QtyModel(field1 = Decimal('123456789.12'))
		m.save()
		
		m2 = QtyModel.objects.get(pk = m.id)
		self.assertEqual(m2.field1, Decimal('123456789.12'))
	
	def test_short_message(self):
		m = ShortMessageModel(field1 = '*' * 140)
		m.save()
	
	def test_short_name(self):
		m = ShortNameModel(field1 = '*' * 50)
		m.save()
	
	def test_uuid(self):
		m = UUIDModel()
		m2 = UUIDModel()
		
		self.assertEqual(m.field1, '', "UUID field should start blank")
		m.save()
		m2.save()
		
		self.assertNotEqual(m.field1, '', "UUID field should not be blank after saving")
		self.assertNotEqual(m.field1, m2.field1, "Two uuid fields should not be the same")
		
		
if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
