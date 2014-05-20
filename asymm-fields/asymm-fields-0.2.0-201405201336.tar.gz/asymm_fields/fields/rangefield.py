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

import django
from django.db.models import IntegerField

if django.get_version() < '1.6':
	class IntegerRangeField(IntegerField):
		def __init__(self, *args, **kwargs):
			self.min_value = kwargs.pop('min_value', 0)
			self.max_value = kwargs.pop('max_value', None)
			
			super(IntegerRangeField, self).__init__(*args, **kwargs)
			
		def formfield(self, **kwargs):
			defaults = {
				'min_value': self.min_value,
				'max_value': self.max_value,
			}
			defaults.update(kwargs)
			return super(IntegerRangeField, self).formfield(**defaults)
		
		def widget_attrs(self, widget):
			attrs = super(IntegerRangeField, self).widget_attrs(widget)
			if self.min_value is not None:
				attrs['min'] = self.min_value
			if self.max_value is not None:
				attrs['max'] = self.max_value
			return attrs
	
	try:
		from south.modelsinspector import add_introspection_rules
		
		add_introspection_rules([], ['^asymm_fields\.fields\.rangefield\.IntegerRangeField'])
	except ImportError:
		pass

else:
	IntegerRangeField = IntegerField