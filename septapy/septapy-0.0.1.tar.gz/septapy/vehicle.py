import requests

class Vehicle(object):
    """Represents a single physical vehicle traveling along a Route."""

    def __init__(self, jsonArgs, route=None):

        self.latitude    = float(jsonArgs['lat'])
        self.longitude   = float(jsonArgs['lng'])
        self.coords      = (self.latitude, self.longitude)

        self.vehicleID   = jsonArgs['VehicleID']
        self.blockID     = jsonArgs['BlockID']
        self.label       = jsonArgs['label']
        self.direction   = jsonArgs['Direction']

        self.title       = self.label
        self.offset      = jsonArgs['Offset']
        self.destination = jsonArgs['destination']
        self.route       = route

    def __unicode__(self):
        representation = """\
Route: %(route)s
Current location: %(lat)s, %(long)s
Heading: %(heading)s
Next stop: %(destination)s
""" % {
                'route': self.route,
                'lat': self.latitude,
                'long': self.longitude, 
                'heading': self.direction,
                'destination': self.destination,
                }

        return representation

def getVehiclesByRoute(routeIdentifier):
    vehicleURL = 'http://www3.septa.org/transitview/bus_route_data/' + routeIdentifier
    r = requests.get(vehicleURL)
    j = r.json()
    vehicles = j[j.keys()[0]]
    return [Vehicle(v, route=routeIdentifier) for v in vehicles]

def getNearestVehicles(latitude, longitude, route=None):
    vehicles = getVehiclesByRoute(route)
    vehicles.sort(key=lambda v: utils.getDistance(v.latitude, v.longitude, latitude, longitude))
    return vehicles

def getNearestVehicle(latitude, longitude, route=None):
    return getNearestVehicles(latitude, longitude, route)[0]

