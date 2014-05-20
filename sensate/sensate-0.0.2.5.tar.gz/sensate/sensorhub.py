from datetime import datetime
from json import loads, dumps

from sensorcheck import SensorCheck

# TODO: make equipment swappable (when more equipment presents itself)
from equipment.wsg30 import get_sensor_oid
from transports.snmp import SNMPobject

# MAX_SENSORS_PER_HUB restricts SNMP guesswork to a reasonable level.
# (theoretical max # of sensors per WSG30 hub = 30 wireless + 1 Power + 1 Battery.)
MAX_SENSORS_PER_HUB = 32 


class SensorHub(object):
    '''The central communications hub that sensors report back to. 

    Uses SNMP to poll the hub directly over the network. 
    
    Required argument:  
    
    hostname                -- (string) fqdn or LAN-routable hostname (no protocol prefix)
    
    Optional keyword arguments:
    
    match           -- (string) restrict results to only those sensors with `match` in their name
    auto            -- (bool) whether to perform SNMP connections immediately (default: True)
    port            -- (int) port used to connect via snmp (default: 161)
    timeout         -- (int or float) time in seconds to wait for SNMP response.
    retries			-- (int) number of times to retry connection (default: 0)
    snmp_method     -- (string) if pysnmp isn't working for you, try 'cli' (default: 'pysnmp')
    
    Currently decoration-only attributes that can be set by keyword arguments:
    
    model           -- (string) defines model of Sensaphone equipment (default: WSG30)
    ''' 
    
    def __init__(self, hostname, **kwargs):
        '''
        Constructor for SensorHub.

        Uses SNMP to poll the hub directly over the network.
           
        Supply "match" to restrict results to only those sensors
        with "match" in their name.

        :param hostname: (required) fqdn or reachable local hostname.
        :param match: (optional) only load sensors where match (string) can be found in name.
        '''
    
        self.hostname = hostname        
        self.match = kwargs.get('match', '')
        self.model = str(kwargs.get('model', 'WSG30')).upper()
        
        # whether to complete SNMP checks immediately
        auto = kwargs.get('auto', True)
        
        ## SNMP ##
        self.snmp_method = kwargs.get('snmp_method', 'pysnmp')
        self.retries = kwargs.get('retries', 0)
        # generic timeout length in seconds for any type of connection.
        self.timeout = kwargs.get('timeout', 10)  
        
        # Updated every time snmp_check_sensors used.
        self.lastchecktime = None

        # Assign self.snmp_get to a generated snmp get function.  
        self.snmp_get = SNMPobject(hostname=self.hostname, timeout=self.timeout,
            			retries=self.retries, method=self.snmp_method).snmp_getter()

        self.sensors_by_idx = {}   # idx: name mapping. Filled during discover()
        self.checks_by_idx = {}    # idx: SensorCheck mapping. Filled during check()
        self.checks = []

        if auto:
            self.reload()

    def check(self):
        '''Populates and returns self.checks by retrieving SensorCheck objects via SNMP (destructive update)
        
        Also sets up self.checks_by_idx (idx to SensorCheck mapping) because I can't decide. :P
        
        :rtype: list of SensorCheck objects
        ''' 
        self.checks = []
        self.checks_by_idx = {}
        for idx in self.sensors_by_idx.keys():
            checktime = datetime.utcnow()
            check = SensorCheck.from_snmp(self.hostname, idx, name=self.sensors_by_idx[idx], checktime=checktime)
            self.checks.append(check)
            self.checks_by_idx[idx] = check
        return self.checks

    def discover(self):
        '''Populates and returns self.sensors_by_idx (destructive update)
        
        :rtype: dictionary mapping of sensor index (int) to name (str) 
        '''
        self.sensors_by_idx = {} 
        self.lastchecktime = datetime.utcnow()
        
        for idx in range(MAX_SENSORS_PER_HUB+1):
            name = self.snmp_get(get_sensor_oid(idx, 'name'))
            # we sometimes get garbage characters in the sensor name :(
            try:
                name.decode()
            except UnicodeDecodeError, e:
                #TODO: CONVERT name (don't just give up on it)
                #logger.debug(e)
                continue
            except AttributeError, e:
                # name was returned as None
                #logger.debug(e)
                continue

            if self.match:
                if self.match in name:
                    self.sensors_by_idx[idx] = name
            else:
                if name and name != 'Unconfigured':
                    self.sensors_by_idx[idx] = name
        return self.sensors_by_idx
                    
    def reload(self):
        '''Convenience interface to self.discover() and self.check()'''
        self.discover()
        self.check()
    
    def __str__(self):
        out = 'Sensaphone Hub at %s\n\n' % self.hostname
        for idx in sorted(self.sensors_by_idx.keys()):
            out += '%d: %s\n' % (idx, self.sensors_by_idx[idx])
        return out
