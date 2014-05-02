#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generic PPS Data (products and intermediate data products) reader
"""

import version

__version__ = version.__version__

import h5py
from datetime import datetime, timedelta
import numpy as np

import logging
LOG = logging.getLogger(__name__)


class InfoObject(object):
    """Simple data and info container.
    """
    def __init__(self):
        self.info = {}
        self.data = None

class NwcSafPpsData(object):
    """The NWCSAF PPS Data class providing the readers"""
    def __init__(self, filename=None):
        self.info = {}
        self._how = {}
        self._what = {}
        self.lon = None
        self.lat = None

        self._md = {}
        self._projectables = []
        self._keys = []
        self._refs = {}
        self.shape = None
        if filename:
            with h5py.File(filename, "r") as h5f:
                if 'how' in h5f.keys() or 'where' in h5f.keys() or 'what' in h5f.keys():
                    self.read_odim(filename)
                else:
                    self.read(filename)

    def read_odim(self, filename, load_lonlat=True):
        """Read pps hdf5 odim formatet data from *filename*. 
        """

        h5f = h5py.File(filename, "r")

        # Read the /how attributes

        self._how = dict(h5f['how'].attrs)
        self._what = dict(h5f['what'].attrs)
        if 'platform' in h5f['how'].attrs.keys():
            self._how["satellite"] = h5f['how'].attrs['platform']
        else:
            LOG.warning('No platform in how group. Skipping...')
        # Which one to use?:
        self._how["time_slot"] = (timedelta(seconds=long(h5f['how'].attrs['startepochs']))
                                  + datetime(1970, 1, 1, 0, 0))
        self._what["time_slot"] = datetime.strptime(h5f['what'].attrs['date'] + 
                                                    h5f['what'].attrs['time'],
                                                    "%Y%m%d%H%M%S")

         # Read the data and attributes
        #   This covers only one level of data. This could be made recursive.
        for key, dataset in h5f.iteritems():
            if "how" in dataset.name or "what" in dataset.name:
                continue
                
            if "image" in dataset.name:
                setattr(self, key, InfoObject())
                getattr(self, key).info = dict(dataset.attrs)
                getattr(self, key).data = dataset['data'][:]

                if not self.shape:
                    self.shape = getattr(self, key).data.shape

                if 'how' in dataset:
                    for skey, value in dataset['how'].attrs.iteritems():
                        getattr(self, key).info[skey] = value
                if 'what' in dataset:                    
                    for skey, value in dataset['what'].attrs.iteritems():
                        getattr(self, key).info[skey] = value


            if "where" in dataset.name and load_lonlat:
                setattr(self, 'lon', InfoObject())
                getattr(self, 'lon').data = h5f['/where/lon/data'][:]
                getattr(self, 'lon').info = dict(dataset.attrs)
                for skey, value in dataset['lon/what'].attrs.iteritems():
                    getattr(self, 'lon').info[skey] = value

                setattr(self, 'lat', InfoObject())
                getattr(self, 'lat').data = h5f['/where/lat/data'][:]
                getattr(self, 'lat').info = dict(dataset.attrs)
                for skey, value in dataset['lat/what'].attrs.iteritems():
                    getattr(self, 'lat').info[skey] = value

                if not self.shape:
                    self.shape = self.lon.data.shape

        h5f.close()

        if not load_lonlat:
            return

        # Setup geolocation
        try:
            from pyresample import geometry
        except ImportError:
            return

        if hasattr(self, "lon") and hasattr(self, "lat"):
            lons = self.lon.data * self.lon.info["gain"] + self.lon.info["gain"]
            lats = self.lat.data * self.lat.info["gain"] + self.lat.info["gain"]
            self.area = geometry.SwathDefinition(lons=lons, lats=lats)
        else:
            LOG.warning("No longitudes or latitudes for data")

        return

    def read(self, filename):
        """Read pps hdf5 formatet data from *filename*. Does not support ODIM
        format (yet), only old flat-style PPS format. For PPS in ODIM format
        use *read_odim*

        This reader does not yet support the extraction of geolocation
        data. The longitudes and latitudes are supposed to be extracted from
        separate ODIM style PPS files (avhrr/viirs and sunsatangles files)
        """

        h5f = h5py.File(filename, "r")

        # Read the global attributes

        self._md = dict(h5f.attrs)
        try:
            self._md["satellite"] = h5f.attrs['satellite_id']
            self.info["satellite"] = h5f.attrs['satellite_id']
        except KeyError:
            LOG.warning("No root level attribute like this: satellite_id")
        try:
            self._md["orbit"] = h5f.attrs['orbit_number']
            self.info["orbit_number"] = h5f.attrs['orbit_number']
        except KeyError:
            LOG.warning("No root level attribute like this: orbit_number")
        try:
            self._md["time_slot"] = (timedelta(seconds=long(h5f.attrs['sec_1970']))
                                     + datetime(1970, 1, 1, 0, 0))
            self.info['time'] = self._md["time_slot"]
        except KeyError:
            LOG.warning("No root level attribute like this: sec_1970")

        # Read the data and attributes
        #   This covers only one level of data. This could be made recursive.
        for key, dataset in h5f.iteritems():
            if key.startswith('1'):
                key = 'one' + key.strip('1')

            setattr(self, key, InfoObject())
            getattr(self, key).info = dict(dataset.attrs)
            for skey, value in dataset.attrs.iteritems():
                if isinstance(value, h5py.h5r.Reference):
                    self._refs[(key, skey)] = h5f[value].name.split("/")[1]
                    
            if type(dataset.id) is h5py.h5g.GroupID:
                LOG.warning("Format reader does not support groups")
                continue

            try:
                getattr(self, key).data = dataset[:]
                is_palette = (dataset.attrs.get("CLASS", None) == "PALETTE")
                if(len(dataset.shape) > 1 and
                   not is_palette and
                   key not in ["lon", "lat", 
                               "row_indices", "column_indices"]):
                    self._projectables.append(key)
                    if self.shape is None:
                        self.shape = dataset.shape
                    elif self.shape != dataset.shape:
                        raise ValueError("Different variable shapes !")
                else:
                    self._keys.append(key)
            except TypeError:
                setattr(self, key, np.dtype(dataset))
                self._keys.append(key)

        h5f.close()

