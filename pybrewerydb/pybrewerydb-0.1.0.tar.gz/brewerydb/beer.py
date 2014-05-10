class Beer(object):
    resource_url = 'beer'
    
    def __init__(self, data):
        self.data = data

    def __unicode__(self):
        return self.name
        
    @property
    def name(self):
        return self.data['name']
    
    @property
    def id(self):
        return self.data['id']
    
    @property
    def abv(self):
        return self.data['abv']
    
    @property
    def ibu(self):
        return self.data['ibu']
    
    @property
    def description(self):
        return self.data['description']
    
    @property
    def organic(self):
        if self.data['isOrganic'] == 'Y':
            return True
        return False
    
    @property
    def label_images(self):
        return {'large': self.data['labels']['large'],
                'medium': self.data['labels']['medium']}
    
    @property
    def brewery_id(self):
        return self.data['breweries'][0]['id']
    
    
    
class Beers(Beer):
    resource_url = 'beers'