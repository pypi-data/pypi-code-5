from common import Resource

class StatsApi(Resource):

    def __init__(self, api):
        super(StatsApi, self).__init__(api)
    	self.uri = 'stats'
    	self.version = 'v1.2'
    	self.available_regions = ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce']

    def get_ranked_stats(self, sid):
        path = u'/api/lol/%s/%s/stats/by-summoner/%s/ranked' % (self.api.region, self.version, sid)
        return self.get(path)

    def get_summary(self, sid):
        path = u'/api/lol/%s/%s/stats/by-summoner/%s/summary' % (self.api.region, self.version, sid)
        return self.get(path)