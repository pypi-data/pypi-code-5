from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text

from . import Geoposition, GeoBoundingBox
from .forms import GeopositionField as GeopositionFormField, GeoBoundingBoxField as GeoBoundingBoxFormField


class GeopositionField(models.Field):
    description = _("A geoposition (latitude and longitude)")
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 42
        super(GeopositionField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        if not value or value == 'None':
            return None
        if isinstance(value, Geoposition):
            return value
        if isinstance(value, list):
            return Geoposition(value[0], value[1])

        # default case is string
        value_parts = value.rsplit(',')
        try:
            latitude = value_parts[0]
        except IndexError:
            latitude = '0.0'
        try:
            longitude = value_parts[1]
        except IndexError:
            longitude = '0.0'

        return Geoposition(latitude, longitude)

    def get_prep_value(self, value):
        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return smart_text(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': GeopositionFormField
        }
        defaults.update(kwargs)
        return super(GeopositionField, self).formfield(**defaults)


class GeoBoundingBoxField(models.Field):
    description = _("A geo bounding box (latitude and longitude for top left and bottom right corner)")
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 85
        super(GeoBoundingBoxField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        if not value or value == 'None':
            return None
        if isinstance(value, GeoBoundingBox):
            return value
        if isinstance(value, list):
            return GeoBoundingBox(value[0], value[1], value[2], value[3])

        # default case is string
        value_parts = value.split(',')
        try:
            latitude1 = value_parts[0]
        except IndexError:
            latitude1 = '0.0'
        try:
            longitude1 = value_parts[1]
        except IndexError:
            longitude1 = '0.0'
        try:
            latitude2 = value_parts[2]
        except IndexError:
            latitude2 = '0.0'
        try:
            longitude2 = value_parts[4]
        except IndexError:
            longitude2 = '0.0'

        return GeoBoundingBox(latitude1, longitude1, latitude2, longitude2)

    def get_prep_value(self, value):
        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return smart_text(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': GeoBoundingBoxFormField
        }
        defaults.update(kwargs)
        return super(GeoBoundingBoxField, self).formfield(**defaults)
