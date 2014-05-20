import requests


class GeocodeClient(object):

    url = "https://maps.googleapis.com/maps/api/geocode"
    api_type = "json"

    def __init__(self, key, data={}, url=None, api_type=None):
        self.key = key
        self.data = data
        self._prepare_address()
        if url:
            self.url = url
        if api_type:
            self.api_type = api_type

    def _prepare_address(self):
        if u'address' in self.data:
            splitted = [w for w in self.data['address'].split(' ') if w]
            self.data['address'] = u"+".join(splitted)

    def _data_join(self):
        qs_list = [u'{}={}'.format(k, v) for k, v in self.data.items()]
        return u'&'.join(qs_list)

    def uri(self):
        self.data[u'key'] = self.key

        return u'{}/{}?{}'.format(
            self.url,
            self.api_type,
            self._data_join()
        )

    def get(self):
        return requests.get(self.uri())