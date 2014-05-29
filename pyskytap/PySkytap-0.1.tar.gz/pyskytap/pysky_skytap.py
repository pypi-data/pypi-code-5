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
import requests
import json
from .pysky_configuration import configuration
from .pysky_psexception import PSException

from pprint import pprint

##from pysky import PSException

class skytap():

    def __init__(self):
        self.__logged = False
        self.__api_version = None
        self.__session = None
        self.__user = None
        self.__password = None
        self.__headers = { 
            #requesite json headers for API
            'Accept' : 'application/json',
            'Content-Type' : 'application/json'
        }
        self.__auth = None
        self.__server_url = None

    def connect(self, host=None, user=None, password=None, trace_file=None, sock_timeout=None):
        """Opens a session to Skytap with the given credentials:
        @host: is the server's hostname or address. If the web service uses
        another protocol or port than the default, you must use the full
        service URL (e.g. http://myhost:8888/sdk)
        @user: username to connect with
        @password: password to authenticate the session
        @trace_file: (optional) a file path to log requests and responses
        """

        self.__user = user
        self.__password = password
        self.__auth=(self.__user,self.__password)

        #Generate server's URL
        if not isinstance(host, basestring):
            ##raise Exception("host URL error")
            raise PSException("'host' should be a string with the Skytap Cloud SDK url.",FaultTypes.PARAMETER_ERROR)

        elif (host.lower().startswith('http://')
        or host.lower().startswith('https://')):
            self.__server_url = host.lower()

        else:
            self.__server_url = 'https://%s' % host

        ## attempt to make a API call.
        api_response=self._api_get('/users')
        if api_response.status_code==200:
            self.__logged=True
        else:
            self.__logged=False

        return self.__logged
        
    def get_server_url(self):
        return self.__server_url

    def is_connected(self):
        """True if the user has successfuly logged in. False otherwise"""
        return self.__logged

    def disconnect(self):
        if self.__logged:
            self.__logged = False
                
    def get_configuration(self,id):
        api_response=self._api_get('/configurations/' + str(id))
        ##pprint (vars(api_response),indent=4)
        if api_response.status_code==200:
            cfg = configuration(json.loads(api_response.text),self)
            ##cfg.set_skytap_instance(self)
        else:
            cfg = None
        return cfg

    def get_vmid_by_desktopid(self,id):
        api_response=self._api_get('/vms/' + id + '/desktop')
        if api_response.status_code==200:
            ##print json.dumps(my_json, indent = 4)
            my_json=json.loads(api_response.text)
            vm_id=my_json['vms'][0]['vm_ref'].split("/")[-1]
            ##print vm_id
        return vm_id

    def get_configid_by_vmid(self,id):
        api_response=self._api_get('/vms/' + id)
        if api_response.status_code==200:
            ##print json.dumps(my_json, indent = 4)
            my_json=json.loads(api_response.text)
            cfg_id=my_json['configuration_url'].split("/")[-1]
        return cfg_id

    ''' *************************************
    *** HTTP method calls for the Skytap APIs
    ''' 
    def _api_get(self,url_suffix):
        url=self.__server_url + url_suffix    
        
        try:
            api_response = requests.get(url, headers=self.__headers, auth=self.__auth)
            return api_response
        except requests.exceptions.ConnectionError:
            ##raise PSException('message','code')
            return {}

    
    def _api_put(self,url_suffix,params):
        url=self.__server_url + url_suffix    
        api_response = requests.put(url, headers=self.__headers, auth=self.__auth, params=params)
        ##pprint (vars(api_response),indent=4)
        return api_response

    
    def _api_post(self,url_suffix,params):
        url=self.__server_url + url_suffix    
        api_response = requests.post(url, headers=self.__headers, auth=self.__auth, params=params)
        return api_response

    def _api_delete(self,url_suffix,params):
        url=self.__server_url + url_suffix    
        api_response = requests.delete(url, headers=self.__headers, auth=self.__auth, params=params)
        return api_response
 
