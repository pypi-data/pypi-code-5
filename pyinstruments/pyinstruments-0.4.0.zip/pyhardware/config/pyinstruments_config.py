"""
Module used to store and retrieve usefull information in a jsonable file
"""

from pyhardware.drivers.ivi import IviDriver
from pyhardware.drivers.visa import VisaDriver
from pyhardware.drivers.serial import SerialDriver
from pyhardware.utils.class_utils import list_all_child_classes
                
import json
import os
from collections import OrderedDict



class PyInstrumentsConfig(dict):
    """
    Container class to store the configuration informations
    """
    
    def __init__(self):
        self.path = os.path.join(os.environ["HOMEDRIVE"], \
                                 os.environ["HOMEPATH"], \
                                 ".pyinstrument")
        try:
            self.load()
        except IOError:
            super(PyInstrumentsConfig, self).__init__()

    def load(self):
        """load the content from the config file on disk"""
        with open(self.path) as load_file:
            super(PyInstrumentsConfig, self).__init__(json.load(load_file))

    def save(self):
        """Saves the content from the config file on disk"""        
        json.dump(self, open(self.path, 'w'), indent = 0)

    def add_instrument(self, tag="DEV", address=None, model=None, simulate=False, code=""):
        """adds an instrument with the given address and model in the internal
        config file of the module
        """
        
        pic = PyInstrumentsConfig()
        main_tag = tag
        n = 1
        while(tag in pic.keys()):
            tag = main_tag + str(n)
            n += 1
        if model==None:
            model = '???'
        pic[tag] = {"address":address,
                    "model":model,
                    "simulate":simulate,
                    "code":code}
        
        pic[tag]['code'] = pic.autogenerated_code(tag)
        pic.save()
        return tag
        
        
    def remove(self, tag):
        del self[tag]
        self.save()
        
    def autogenerated_code(self, tag):
        """
        returns the autogenerated code given the address and model of a device
        """
        
        
        model = self[tag]['model']
        
        ##1/ check if an IVI driver works
 
        
        string_visa = """from pyhardware.drivers.visa import {0}
instrument = {0}(logical_name, address, simulate, timeout=100)
"""
        
        ###2/ check a visa driver
        for name, visa_driver_type \
                    in list_all_child_classes(VisaDriver).iteritems():
            if model in visa_driver_type.supported_models():
                return string_visa.format(visa_driver_type.__name__)
            
        string_serial = """from pyhardware.drivers.serial import {0}
instrument = {0}(logical_name, address, simulate)
"""           
        ###3/ check a serial driver
        for name, serial_driver_type \
                    in list_all_child_classes(SerialDriver).iteritems():
            if model in serial_driver_type.supported_models():
                return string_serial.format(serial_driver_type.__name__)
        
        string_ivi = """import pyivi
from pyhardware.drivers.ivi import {0}
driver = pyivi.ivi_instrument(address, model=model, simulate=simulate)
instrument = {0}(logical_name, driver)
"""
        
        for name, ivi_driver_type \
                    in list_all_child_classes(IviDriver).iteritems():
            if model in ivi_driver_type.supported_models():
                return string_ivi.format(ivi_driver_type.__name__)
            
        return """no supporting drivers in ivi, visa or serial, sorry..."""