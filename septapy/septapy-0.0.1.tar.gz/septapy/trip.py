import requests

class Trip(object):
    """Represents a list of stops and times for a single Vehicle.

    Has associated attributes such as:
    .latitude
    .longitude
    .coords        # latitude and longitude as tuple
    .route
    """
    
    def __init__(self, jsonArgs, route=None):

        self.tripsURL    = 'http://www3.septa.org/hackathon/TransitView/trips.php?route=' + route
        self.latitude    = jsonArgs['lat']
        self.longitude   = jsonArgs['lng']
        self.coords      = (self.latitude, self.longitude)
        self.label       = jsonArgs['label']

        self.vehicleID   = jsonArgs['VehicleID']
        self.tripID      = jsonArgs['TripID']
        self.blockID     = jsonArgs['BlockID']

        self.direction   = jsonArgs['Direction']
        self.destination = jsonArgs['destination']
        self.offset      = jsonArgs['Offset']

        self.route       = route

    def __str__(self):
        representation = """\
Route: %(route)s
Stop Name: %(stopName)s
Stop ID: %(stopID)s
Location: %(lat)s, %(long)s
""" % {
                'route': self.route,
                'stopName': self.name,
                'stopID': self.stopID, 
                'lat': self.latitude,
                'long': self.longitude,
                }

        return representation

def getTripsByRoute(routeIdentifier):
    tripsURL = 'http://www3.septa.org/hackathon/TransitView/trips.php?route=' + routeIdentifier
    r = requests.get(tripsURL)
    j = r.json()['bus']
    return [Trip(t, route=routeIdentifier) for t in j]
