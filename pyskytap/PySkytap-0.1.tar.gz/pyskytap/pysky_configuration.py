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
from .pysky_vm import vm
## from .pysky_skytap import skytap
from pprint import pprint

class configuration():

    def __init__(self, j_cfg, skytap_instance):
    	## load object
    	self.__cfg = j_cfg
        self.__id = self.__cfg['id']
        self.__owner = self.__cfg['owner']
        self.__name = self.__cfg['name']
        self.__region = self.__cfg['region']
        self.__vms = []
        self.__skytap_instance = skytap_instance

    def owner(self):
        return self.__owner

    def name(self):
        return self.__name

    def region(self):
        return self.__region

    def id(self):
        return self.__id

    def reload(self):
        url_suffix='/configurations/' + str(self.__id)
        api_response=self.__skytap_instance._api_get(url_suffix)
        if api_response.status_code==200:
            self.__cfg = json.loads(api_response.text)
        return api_response
        
    def vms(self):
        vmslist = self.__cfg['vms']
        for a_vm in vmslist:
            vmobj=vm(a_vm,self.__skytap_instance)
            self.__vms.append(vmobj)
        return self.__vms
    
    def raw(self):
        return self.__cfg

    def __str__(self):
    	return json.dumps(self.__cfg,indent=4)
