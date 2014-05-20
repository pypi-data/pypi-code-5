from __future__ import unicode_literals

from decimal import Decimal

VERSION = (0, 2, 0)
__version__ = '.'.join(map(str, VERSION))


class Geoposition(object):
    def __init__(self, latitude, longitude):
        if isinstance(latitude, float) or isinstance(latitude, int):
            latitude = str(latitude)
        if isinstance(longitude, float) or isinstance(longitude, int):
            longitude = str(longitude)

        self.latitude = Decimal(latitude)
        self.longitude = Decimal(longitude)

    def __str__(self):
        return "%s,%s" % (self.latitude, self.longitude)

    def __repr__(self):
        return "Geoposition(%s)" % str(self)

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        return isinstance(other, Geoposition) and self.latitude == other.latitude and self.longitude == other.longitude

    def __ne__(self, other):
        return not isinstance(other, Geoposition) or self.latitude != other.latitude or self.longitude != other.longitude


class GeoBoundingBox(object):
    def __init__(self, latitude1, longitude1, latitude2, longitude2):
        if isinstance(latitude1, float) or isinstance(latitude1, int):
            latitude = str(latitude1)
        if isinstance(longitude1, float) or isinstance(longitude1, int):
            longitude = str(longitude1)
        if isinstance(latitude2, float) or isinstance(latitude2, int):
            latitude = str(latitude2)
        if isinstance(longitude2, float) or isinstance(longitude2, int):
            longitude = str(longitude2)

        self.latitude1 = Decimal(latitude1)
        self.longitude1 = Decimal(longitude1)
        self.latitude2 = Decimal(latitude2)
        self.longitude2 = Decimal(longitude2)

    def __str__(self):
        return "%s,%s,%s,%s" % (self.latitude1, self.longitude1, self.latitude2, self.longitude2)

    def __repr__(self):
        return "GeoBoundingBox(%s)" % str(self)

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        return isinstance(other, GeoBoundingBox) and \
            self.latitude1 == other.latitude1 and \
            self.longitude1 == other.longitude1 and \
            self.latitude2 == other.latitude2 and \
            self.longitude2 == other.longitude2

    def __ne__(self, other):
        return not isinstance(other, GeoBoundingBox) or \
            self.latitude1 != other.latitude1 or \
            self.longitude1 != other.longitude1 or \
            self.latitude2 != other.latitude2 or \
            self.longitude2 != other.longitude2
