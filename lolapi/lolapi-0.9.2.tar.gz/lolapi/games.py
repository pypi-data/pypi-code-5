from common import Resource

class GamesApi(Resource):

    def __init__(self, api):
        super(GamesApi, self).__init__(api)
    	self.version = 'v1.3'
    	self.available_regions = ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce']

    def get_recent(self, sid):
        path = u'/api/lol/%s/%s/game/by-summoner/%s/recent' % (self.api.region, self.version, sid)
        return self.get(path)