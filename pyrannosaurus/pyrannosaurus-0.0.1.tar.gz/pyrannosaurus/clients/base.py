import string
import sys
import os.path

from suds.client import Client
from suds.cache import FileCache

from pyrannosaurus import get_package_dir

class BaseClient(object):
    '''
        LoginClient uses suds to wrap the SF partner wsdl, but really only uses
        the login method
    '''

    _sessionHeader = None
    _product = 'Metadata Tool'
    _version = (0, 0, 0)
    _location = None

    _loginScopeHeader = None
    _base_client = None
    _client = None

    def __init__(self, wsdl='wsdl/partner.xml', cacheDuration = 0, **kwargs):
        print "super"
        if cacheDuration > 0:
            cache = FileCache()
            cache.setduration(seconds = cacheDuration)
        else:
            cache = None

        wsdl = get_package_dir(wsdl)
        wsdl = 'file:///' + os.path.abspath(wsdl)
        self._base_client =  Client(wsdl, cache = cache)

        headers = {'User-Agent': 'Salesforce/' + self._product + '/' + '.'.join(str(x) for x in self._version)}
        self._base_client.set_options(headers = headers)

    def _login(self, username, password, token='', is_production=False):
        self._setHeaders('login')
        target_url = 'https://login.salesforce.com/services/Soap/u/29.0' if is_production else 'https://test.salesforce.com/services/Soap/u/29.0'
        self._base_client.set_options(location=target_url)
        result = self._base_client.service.login(username, password + token)
        header = self.generateHeader('SessionHeader')
        header.sessionId = result['sessionId']
        self.setSessionHeader(header)
        self._sessionId = result['sessionId']

        return result

    #TODO : this really won't work, needs check for sobjecttype to go to right client
    def generateHeader(self, sObjectType):
        try:
          return self._base_client.factory.create(sObjectType)
        except:
          print 'There is not a SOAP header of type %s' % sObjectType

    #TODO eval
    def _setEndpoint(self, location):
        try:
          self._client.set_options(location = location)
        except:
          self._client.wsdl.service.setlocation(location)

        self._location = location

    #TODO eval
    def _setHeaders(self, call = None):
        headers = {'SessionHeader': self._sessionHeader}

        if call == 'login':
            if self._loginScopeHeader is not None:
                headers['LoginScopeHeader'] = self._loginScopeHeader
            self._base_client.set_options(soapheaders = headers)
        else:
            self._client.set_options(soapheaders = headers)

    #TODO: replace
    def setLoginScopeHeader(self, header):
        self._loginScopeHeader = header

    #TODO: replace
    def setSessionHeader(self, header):
        self._sessionHeader = header

    def set_timeout(self, time):
        self._base_client.set_options(timeout=time)

    def create_object(self, name):
        try:
            return self._client.factory.create(name)
        except:
            #TODO: should be real exception
            return "Object not found"
