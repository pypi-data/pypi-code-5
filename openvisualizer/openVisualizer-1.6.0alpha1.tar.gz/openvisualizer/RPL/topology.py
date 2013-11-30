# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
'''
Module which receives DAO messages and calculates source routes.

.. moduleauthor:: Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>
                  January 2013
.. moduleauthor:: Thomas Watteyne <watteyne@eecs.berkeley.edu>
                  April 2013
'''
import logging
log = logging.getLogger('topology')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading

import openvisualizer.openvisualizer_utils as u
from openvisualizer.eventBus import eventBusClient

class topology(eventBusClient.eventBusClient):
    
    def __init__(self):
        
        # local variables
        self.dataLock        = threading.Lock()
        self.parents         = {}
        
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'topology',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'updateParents',
                    'callback'    : self.updateParents,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getParents',
                    'callback'    : self.getParents,
                },
            ]
        )
    
    #======================== public ==========================================
    
    def getParents(self,sender,signal,data):
        return self.parents
    
    def updateParents(self,sender,signal,data):
        ''' inserts parent information into the parents dictionary '''
        with self.dataLock:
            #data[0] == source address, data[1] == list of parents
            self.parents.update({data[0]:data[1]})
    
    #======================== private =========================================
    
    #======================== helpers =========================================
