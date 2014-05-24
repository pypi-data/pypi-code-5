from common import Resource

class ChampionsApi(Resource):

    def __init__(self, api):
        super(ChampionsApi, self).__init__(api)
    	self.version = 'v1.1'
    	self.available_regions = ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce']

    def get_all(self):
        path = u'/api/lol/%s/%s/champion' % (self.api.region, self.version)
        return self.get(path)