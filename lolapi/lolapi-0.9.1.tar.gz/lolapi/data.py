from common import Resource

class StaticDataApi(Resource):

    def __init__(self, api):
        super(StaticDataApi, self).__init__(api)
    	self.uri = 'static-data'
    	self.version = 'v1'
    	self.available_regions = ['br', 'eune', 'euw', 'kr', 'lan', 'las', 'na', 'oce', 'ru', 'tr']

    def get_champions(self):
        path = u'/api/lol/static-data/%s/%s/champion' % (self.api.region, self.version)
        return self.get(path)

    def get_champion_by_id(self, cid):
        path = u'/api/lol/static-data/%s/%s/champion/%s' % (self.api.region, self.version, cid)
        return self.get(path)

    def get_items(self):
        path = u'/api/lol/static-data/%s/%s/item' % (self.api.region, self.version)
        return self.get(path)

    def get_item_by_id(self, iid):
        path = u'/api/lol/static-data/%s/%s/item/%s' % (self.api.region, self.version, iid)
        return self.get(path)

    def get_masteries(self):
        path = u'/api/lol/static-data/%s/%s/mastery' % (self.api.region, self.version)
        return self.get(path)

    def get_mastery_by_id(self, mid):
        path = u'/api/lol/static-data/%s/%s/mastery/%s' % (self.api.region, self.version, mid)
        return self.get(path)

    def get_realms(self):
        path = u'/api/lol/static-data/%s/%s/realm' % (self.api.region, self.version)
        return self.get(path)

    def get_runes(self):
        path = u'/api/lol/static-data/%s/%s/rune' % (self.api.region, self.version)
        return self.get(path)

    def get_rune_by_id(self, rid):
        path = u'/api/lol/static-data/%s/%s/rune/%s' % (self.api.region, self.version, rid)
        return self.get(path)

    def get_summoner_spells(self):
        path = u'/api/lol/static-data/%s/%s/summoner-spell' % (self.api.region, self.version)
        return self.get(path)

    def get_summoner_spell_by_id(self, sid):
        path = u'/api/lol/static-data/%s/%s/summoner-spell/%s' % (self.api.region, self.version, sid)
        return self.get(path)