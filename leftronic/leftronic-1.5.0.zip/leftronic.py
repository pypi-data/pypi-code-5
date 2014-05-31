import urllib2
import json
import logging

try:
    from Crypto.Cipher import AES
    from Crypto import Random
    import base64
except:
    print ('Could not import the PyCrypto library. Please `pip install '
           'pycrypto` if you wish to encrypt your outgoing data.')

logger = logging.getLogger(__name__)


class Leftronic(object):
    """
    Provides access to Leftronic Custom Data API
    """

    __version__ = '1.5.0'

    def __init__(self, auth_key):
        self.access_key = auth_key
        self.api_url = 'https://www.leftronic.com/customSend'
        self.crypto_key = None

    def setEncryptionKey(self, crypto_key):
        self.crypto_key = crypto_key

    def pushMultiple(self, points):
        """
        Pushes points to multiple streams.  Points is a list of dicts
        as returned by the `populate` methods provided below.

        e.g., pushMultiple([populateNumber("MyNumber", 42),
                            populateGeo("MyMap", 34, -118)])
        """
        if type(points) != list:
            raise TypeError('You must pass in a list')
        else:
            return self.postData({"streams": points})

    def pushNumber(self, stream_name, point):
        """
        Pushes a number (or list of numbers) to a Number, Horizontal/Vertical
        Bar, Dial widget, Stoplight or sparkline/line graph
        """
        return self.postData(self.populateNumber(stream_name, point))

    def populateNumber(self, stream_name, point):
        """
        Formats the provided number, list of numbers, or dict of
        numbers as a Python dict, e.g., to be pushed along with other
        streams.
        """
        if type(point) == float or type(point) == long or type(point) == int:
            point = {'number': point}
        elif type(point) == list:
            last = 0
            for i in point:
                if int(i['timestamp']) > last:
                    last = int(i['timestamp'])
                else:
                    # Timestamp values must increase
                    raise ValueError('Timestamp values must increase')
        elif type(point) == dict:
            pass
        else:
            raise TypeError('You must pass in a numeric value, a list, or a '
                            'dict')
        return {'streamName': stream_name, 'point': point}

    def pushGeo(self, stream_name, lat, lon, color=None):
        """
        Pushes a geographic location (latitude and longitude) to a Map
        widget.  Color can also be passed (red, green, blue, yellow,
        or purple).

        Default color is red.
        """
        return self.postData(self.populateGeo(stream_name, lat, lon, color))

    def populateGeo(self, stream_name, lat, lon, color=None):
        """
        Formats a geographic location (latitude and longitude) as a
        dict, e.g., to be supplied to 'pushMultiple()` Color can also
        be passed (red, green, blue, yellow, or purple).

        Default color is red.
        """
        if type(lat) != list and type(lon) != list and type(color) != list:
            point = {'latitude': lat, 'longitude': lon}
            if color:
                point['color'] = color

        elif type(lat) == list and type(lon) == list:
            if len(lat) != len(lon):
                raise ValueError('Your lists of latitudes and longitudes must '
                                 'be the same size.')
            point = []
            for i in range(len(lat)):
                obj = {'latitude': lat[i], 'longitude': lon[i]}
                if color and type(color) == list and color[i]:
                    obj['color'] = color[i]
                point.append(obj)
        else:
            raise TypeError('Your latitude, longitude, or color were not '
                            'properly formatted.')
        return {'streamName': stream_name, 'point': point}

    def pushText(self, stream_name, my_title, my_msg, img_url=None):
        """
        Pushes a title and message to a Text Feed widget.
        """
        return self.postData(self.populateText(stream_name, my_title,
                                               my_msg, img_url))

    def populateText(self, stream_name, my_ttle, my_msg, img_url=None):
        """
        Formats a title and message for a Text Feed widget as a dict,
        which can be passed to `pushMultiple()`
        """
        if (type(my_ttle) != list and
                type(my_msg) != list and
                type(img_url) != list):
            point = {'title': my_ttle, 'msg': my_msg}
            if img_url:
                point['imgUrl'] = img_url
        elif type(my_ttle) == list and type(my_msg) == list:
            if len(my_ttle) != len(my_msg):
                raise ValueError
            point = []
            for i in range(len(my_ttle)):
                obj = {'title': my_ttle[i], 'msg': my_msg[i]}
                if img_url and type(img_url) == list and img_url[i]:
                    obj['imgUrl'] = img_url[i]
                point.append(obj)
        else:
            raise TypeError

        return {'streamName': stream_name, 'point': point}

    def pushLeaderboard(self, stream_name, leader_array):
        """ Pushes an array to a Leaderboard widget. """
        return self.postData(self.populateLeaderboard(stream_name,
                                                      leader_array))

    def populateLeaderboard(self, stream_name, leader_array):
        """
        Formats a leaderboard array as a dict for, e.g., passing to
        `pushMultiple()`
        """
        return {'streamName': stream_name,
                'point': {
                    'leaderboard': leader_array
                }}

    def pushList(self, stream_name, list_array):
        """ Pushes an array to a List widget. """
        return self.postData(self.populateList(stream_name, list_array))

    def populateList(self, stream_name, list_array):
        """
        Formats a list as a dict to be pushed using, e.g., `pushMultiple()`.
        """
        if type(list_array) != list:
            raise TypeError
        for i in range(len(list_array)):
            if type(list_array[i]) != dict:
                list_array[i] = {'listItem': list_array[i]}

        return {'streamName': stream_name,
                'point': {
                    'list': list_array
                }}

    def pushPair(self, stream_name, x, y):
        """ Pushes an x,y pair to a Pair widget"""
        return self.postData(self.populatePair(stream_name, x, y))

    def populatePair(self, stream_name, x, y):
        """
        Formats an x, y pair (or lists of x, y pairs) as
        """
        if type(x) == list and type(y) == list:
            point = []
            if len(x) != len(y):
                raise ValueError
            for i in range(len(x)):
                point.append({'x': x[i], 'y': y[i]})
        else:
            point = {'x': x, 'y': y}
        return {'streamName': stream_name,
                'point': point}

    def pushImage(self, stream_name, img_url):
        """ Pushes an image to an Image widget"""
        return self.postData(self.populateImage(stream_name, img_url))

    def populateImage(self, stream_name, img_url):
        """
        Formats a provided image url as a dict to be pushed using, e.g.,
        `pushMultiple()`
        """
        point = {'imgUrl': img_url}
        return {'streamName': stream_name,
                'point': point}

    def pushLabel(self, stream_name, label):
        """ Pushes a label to a Label widget"""
        return self.postData(self.populateLabel(stream_name, label))

    def populateLabel(self, stream_name, label):
        """
        Formats a label as a dict
        """
        point = {'label': label}
        return {'streamName': stream_name,
                'point': point}

    def pushTable(self, stream_name, header_row, data_rows):
        """ Pushes a table to a Table widget """
        return self.postData(self.populateTable(stream_name,
                                                header_row,
                                                data_rows))

    def populateTable(self, stream_name, header_row, data_rows):
        data_rows.insert(0, header_row)
        point = {'table': data_rows}
        return {'streamName': stream_name,
                'point': point}

    def pushHtml(self, stream_name, html_string):
        """
        Pushes HTML to an HTML widget.
        """
        return self.postData(self.populateHtml(stream_name, html_string))

    def populateHtml(self, stream_name, html):
        return {'streamName': stream_name,
                'point': {'html': html}}

    def clear(self, stream_name):
        parameters = {'streamName': stream_name,
                      'command': 'clear'}
        return self.postData(parameters)

    def postData(self, parameters):
        """ Makes an HTTP POST to the API URL. """
        # add the access key
        parameters['accessKey'] = self.access_key

        if self.crypto_key:
            self.encryptStreams(parameters)

        # Convert to JSON
        json_data = json.dumps(parameters)

        logger.debug(json_data)
        # Make request
        response = urllib2.urlopen(self.api_url, json_data)
        return response.read()

    def encryptText(self, text):
        # set up AES encryption
        iv = Random.get_random_bytes(16)
        key = self.crypto_key
        # pad key with spaces if its length is not a multiple of 16
        # note that for extra security the user should not choose a short key
        if len(key) % 16 != 0:
            key += ' ' * (16 - len(key) % 16)
        aes = AES.new(key, AES.MODE_CFB, iv, segment_size=128)

        # also pad text with spaces if length is not a multiple of 16
        if len(text) % 16 != 0:
            text += ' ' * (16 - len(text) % 16)

        enc = aes.encrypt(text)

        # concatenate encrypted text with random iv
        return base64.b64encode(enc) + ':' + base64.b64encode(iv)

    def encryptStreams(self, parameters):
        if 'streams' in parameters:
            for stream in parameters['streams']:
                # encrypt the 'point'
                if type(stream['point']) == list:
                    raise TypeError('If using encryption, your stream "points"'
                                    ' must not be arrays, but single values.')

                stream['epoint'] = self.encryptText(json.dumps(
                                                    stream['point']))

                del stream['point']

        else:
            if type(parameters['point']) == list:
                raise TypeError('If using encryption, your stream "points" '
                                'must not be arrays, but single values.')

            parameters['epoint'] = self.encryptText(json.dumps(
                                                    parameters['point']))
            del parameters['point']
