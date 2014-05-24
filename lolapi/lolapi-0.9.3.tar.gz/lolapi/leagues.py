from common import Resource

class LeaguesApi(Resource):

    def __init__(self, api):
        super(LeaguesApi, self).__init__(api)
    	self.uri = 'league'
    	self.version = 'v2.3'
    	self.available_regions = ['br', 'eune', 'euw', 'na', 'tr']

    def get_by_summoner(self, sid):
        path = u'/api/lol/%s/%s/league/by-summoner/%s' % (self.api.region, self.version, sid)
        return self.get(path)

    def get_entry_by_summoner(self, sid):
        path = u'/api/lol/%s/%s/league/by-summoner/%s/entry' % (self.api.region, self.version, sid)
        return self.get(path)

    def get_by_team(self, tid):
        path = u'/api/lol/%s/%s/league/by-team/%s' % (self.api.region, self.version, tid)
        return self.get(path)

    def get_entry_by_team(self, tid):
        path = u'/api/lol/%s/%s/league/by-team/%s/entry' % (self.api.region, self.version, tid)
        return self.get(path)

    def get_challenger(self):
        path = u'/api/lol/%s/%s/league/challenger' % (self.api.region, self.version)
        return self.get(path)