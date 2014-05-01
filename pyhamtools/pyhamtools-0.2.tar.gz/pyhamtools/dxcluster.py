__author__ = 'dh1tw'

from datetime import datetime
from time import strptime, mktime
import re

import pytz

from pyhamtools.consts import DXSpot as dxspot


UTC = pytz.UTC



def decode_char_spot(raw_string):
    """Chop Line from DX-Cluster into pieces and return a dict with the spot data"""

    data = {}

    # Spotter callsign
    if re.match('[A-Za-z0-9\/]+[:$]', raw_string[6:15]):
        data[dxspot.SPOTTER] = re.sub(':', '', re.match('[A-Za-z0-9\/]+[:$]', raw_string[6:15]).group(0))
    else:
        raise ValueError

    if re.search('[0-9\.]{5,12}', raw_string[10:25]):
        data[dxspot.FREQUENCY] = float(re.search('[0-9\.]{5,12}', raw_string[10:25]).group(0))
    else:
        raise ValueError

    data[dxspot.DX] = re.sub('[^A-Za-z0-9\/]+', '', raw_string[26:38])
    data[dxspot.COMMENT] = re.sub('[^\sA-Za-z0-9\.,;\#\+\-!\?\$\(\)@\/]+', ' ', raw_string[39:69]).strip()
    data[dxspot.TIME] = datetime.now().replace(tzinfo=UTC)

    return data

def decode_pc11_spot(raw_string):
    """Decode DX Spots from PC11 spider messages"""

    data = {}

    spot = raw_string.split("^")
    data[dxspot.FREQUENCY] = float(spot[1])
    data[dxspot.DX] = spot[2]
    data[dxspot.TIME] = datetime.fromtimestamp(mktime(strptime(spot[3]+" "+spot[4][:-1], "%d-%b-%Y %H%M")))
    data[dxspot.COMMENT] = spot[5]
    data[dxspot.SPOTTER] = spot[6]
    data["node"] = spot[7]
    data["raw_spot"] = raw_string
    return data


def decode_pc61_spot(raw_string):
    """Decode DX Spots from PC61 spider messages"""

    data = {}

    spot = raw_string.split("^")
    data[dxspot.FREQUENCY] = float(spot[1])
    data[dxspot.DX] = spot[2]
    data[dxspot.TIME] = datetime.fromtimestamp(mktime(strptime(spot[3]+" "+spot[4][:-1], "%d-%b-%Y %H%M")))
    data[dxspot.COMMENT] = spot[5]
    data[dxspot.SPOTTER] = spot[6]
    data["node"] = spot[7]
    data["ip"] = spot[8]
    data["raw_spot"] = raw_string
    return data
