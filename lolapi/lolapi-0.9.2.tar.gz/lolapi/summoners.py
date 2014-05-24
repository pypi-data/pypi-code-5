from common import Resource

class SummonersApi(Resource):

    def __init__(self, api):
        super(SummonersApi, self).__init__(api)
    	self.version = 'v1.3'
    	self.available_regions = ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce']

    def get_by_names(self, names):
        path = u'/api/lol/%s/%s/summoner/by-name/%s' % (self.api.region, self.version, u','.join(names))
        return self.get(path)

    def get_by_ids(self, sids):
        path = u'/api/lol/%s/%s/summoner/%s' % (self.api.region, self.version, u','.join(sids))
        return self.get(path)

    def get_masteries(self, sids):
        path = u'/api/lol/%s/%s/summoner/%s/masteries' % (self.api.region, self.version, u','.join(sids))
        return self.get(path)

    def get_names(self, sids):
        path = u'/api/lol/%s/%s/summoner/%s/name' % (self.api.region, self.version, u','.join(sids))
        return self.get(path)

    def get_runes(self, sids):
        path = u'/api/lol/%s/%s/summoner/%s/runes' % (self.api.region, self.version, u','.join(sids))
        return self.get(path)