from .brewery import Brewery

class Beer(object):
    resource_url = 'beer'
    
    def __init__(self, data):
        self.data = data

    def __unicode__(self):
        return self.name
        
    @property
    def name(self):
        return self.data.get('name', None)
    
    @property
    def id(self):
        return self.data.get('id', None)
    
    @property
    def abv(self):
        return self.data.get('abv', None)
    
    @property
    def ibu(self):
        return self.data.get('ibu', None)
    
    @property
    def description(self):
        return self.data.get('description', None)
    
    @property
    def organic(self):
        if self.data['isOrganic'] == 'Y':
            return True
        return False
    
    @property
    def year(self):
        return self.data.get('year', None)
    
    @property
    def style(self):
        return self.data['style']['name']
    
    @property
    def label_image_large(self):
        return self.data['labels']['large']
    
    @property
    def label_image_medium(self):
        return self.data['labels']['medium']
    
    @property
    def brewery_id(self):
        return self.data['breweries'][0]['id']
    
    @property
    def brewery(self):
        return Brewery(self.data['breweries'][0])
    
    
class Beers(Beer):
    resource_url = 'beers'