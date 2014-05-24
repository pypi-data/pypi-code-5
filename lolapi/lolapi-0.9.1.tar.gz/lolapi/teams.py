from common import Resource

class TeamsApi(Resource):

    def __init__(self, api):
        super(TeamsApi, self).__init__(api)
    	self.version = 'v2.2'
    	self.available_regions = ['br', 'eune', 'euw', 'na', 'tr']

    def get_by_summoner(self, sid):
        path = u'/api/lol/%s/%s/team/by-summoner/%s' % (self.api.region, self.version, sid)
        return self.get(path)

    def get_by_id(self, tid):
        path = u'/api/lol/%s/%s/team/%s' % (self.api.region, self.version, tid)
        return self.get(path)