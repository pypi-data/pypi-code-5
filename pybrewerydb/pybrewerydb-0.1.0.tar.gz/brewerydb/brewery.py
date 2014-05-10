class Breweries(object):
    resource_url = 'breweries'


class Brewery(object):

    """

    """

    resource_url = 'brewery'

    def __init__(self, data):
        self.data = data

    def __unicode__(self):
        return self.name

    @property
    def id(self):
        return self.data['id']

    @property
    def description(self):
        return self.data['description']

    @property
    def name(self):
        return self.data['name']

    @property
    def established(self):
        return self.data['established']

    @property
    def organic(self):
        if self.data['isOrganic'] == 'Y':
            return True
        return False

    @property
    def website(self):
        return self.data['website']

    @property
    def large_image(self):
        return self.data['images']['large']

    @property
    def medium_image(self):
        return self.data['images']['medium']

