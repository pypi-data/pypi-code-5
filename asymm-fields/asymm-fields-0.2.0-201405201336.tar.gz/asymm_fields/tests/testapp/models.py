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

from django.db import models

from asymm_fields.fields import CommentField, IntegerRangeField, LongMessageField, LongNameField, \
	QtyField, ShortMessageField, ShortNameField, UUIDField

__author__ = "Richard Eames <reames@asymmetricventures.com"
__date__ = "May 20, 2014"
__updated__ = "May 20, 2014"
__rev__ = "$Id$"

class CommentModel(models.Model):
	field1 = CommentField()

class IntegerRangeModel(models.Model):
	field1 = IntegerRangeField()

class LongMessageModel(models.Model):
	field1 = LongMessageField()

class LongNameModel(models.Model):
	field1 = LongNameField()

class QtyModel(models.Model):
	field1 = QtyField()

class ShortMessageModel(models.Model):
	field1 = ShortMessageField()

class ShortNameModel(models.Model):
	field1 = ShortNameField()

class UUIDModel(models.Model):
	field1 = UUIDField()
	
