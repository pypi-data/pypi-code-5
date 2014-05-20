import string
import sys
import os.path

from suds.client import Client
from suds.cache import FileCache

from pyrannosaurus import get_package_dir
from pyrannosaurus.clients.base import BaseClient

class ToolingClient(BaseClient):
    _valid_debug_levels = ['Debug']
    def __init__(self, wsdl='wsdl/tooling.xml', cacheDuration=0, **kwargs):
        super(ToolingClient, self).__init__()
        #TODO: clean this up
        wsdl = get_package_dir(wsdl)
        if ':///' not in wsdl:
            if os.path.isfile(wsdl):
                wsdl = 'file:///' + os.path.abspath(wsdl)

        if cacheDuration > 0:
            cache = FileCache()
            cache.setduration(seconds = cacheDuration)
        else:
            cache = None
        self._client = Client(wsdl, cache = cache)

        headers = {'User-Agent': 'Salesforce/' + self._product + '/' + '.'.join(str(x) for x in self._version)}
        self._client.set_options(headers = headers)
        
    def generateHeader(self, sObjectType):
        try:
          return self._client.factory.create(sObjectType)
        except:
          print 'There is not a SOAP header of type %s' % sObjectType

    def login(self, username, password, token='', is_production=False):
        lr = super(ToolingClient, self)._login(username, password, token, is_production)
        #replace the metadata 'm' with the Tooling 'T'
        url = lr.metadataServerUrl.replace('/m/', '/T/')
        self._setEndpoint(url)
        super(ToolingClient, self)._setEndpoint(lr.serverUrl, base=True)
        super(ToolingClient, self).setSessionHeader(self._sessionHeader)

        return lr

    def get_soap_object(self, obj_name):
        try:
            return self._client.factory.create(obj_name)
        except:
            #TODO: IMPLEMENT REAL EXCEPTION HERE
            print "object not found"

    def create(self, obj):
        self._setHeaders('create')
        resp = self._client.service.create(obj)

        return resp

    def query(self, query):
        self._setHeaders('query')
        resp = self._client.service.query(query)

        return resp

    def execute_anonymous(self, apex):
        self._setHeaders('executeAnonymous')
        execute_anonymous_response = self._client.service.executeAnonymous(apex)

        return execute_anonymous_response