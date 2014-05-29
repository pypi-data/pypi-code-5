#--
# Copyright (c) 2014, Darryl Quinn
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of copyright holders nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#--

import sys
import json
import time
## from .pysky_skytap import skytap
from .pysky_psexception import PSException

from pprint import pprint

class vm():
    def __init__(self, j_vm, skytap_instance):
        self.__vm = j_vm
        self.__id = self.__vm['id']
        self.__name = self.__vm['name']
        self.__runstate = self.__vm['runstate']
        self.__skytap_instance = skytap_instance

    def name(self):
        return self.__name
    
    def id(self):
        return self.__id   

    def reload(self):
        url_suffix='/vms/' + str(self.__id)
        api_response=self.__skytap_instance._api_get(url_suffix)
        if api_response.status_code==200:
            self.__vm = json.loads(api_response.text)
            self.__runstate = self.__vm['runstate']
        return api_response

    def runstate(self):
        self.reload()
        return self.__runstate

    def is_running(self):
        self.reload()
        return (self.__runstate==runstate.RUNNING)

    def is_port_mapped(self, i_port):
        rc=False
        if 'interfaces' in self.__vm:
            for i in self.__vm['interfaces']:
                for s in i['services']:
                    if s['internal_port']==i_port:
                        rc= True
                        break
        return rc

    def map_port(self, i_port):
        url_suffix = '/vms/' + str(self.__id) + '/interfaces/' + self.__vm['interfaces'][0]['id'] + '/services'
        params = {'port':i_port}    
        result = self.__skytap_instance._api_post(url_suffix,params)
        ##time.sleep(10)
        ## retrieve vm json again
        self.reload()
        return result

    def services(self):
        return self.__vm['interfaces'][0]['services']


    def run(self):
        ## call API to set runstate=running
        url_suffix = '/vms/' + str(self.__id)
        params = {'runstate':runstate.RUNNING}    
        result = self.__skytap_instance._api_put(url_suffix,params)
        return result

    def suspend(self):
        ## call API to set runstate=suspended
        url_suffix = '/vms/' + str(self.__id)
        params = {'runstate':runstate.SUSPENDED}    
        result = self.__skytap_instance._api_put(url_suffix,params)
        return result
 
    def __str__(self):
        return json.dumps(self.__vm,indent=4)

class runstate:
    RUNNING = 'running'
    BUSY = 'busy'
    SUSPENDED = 'suspended'