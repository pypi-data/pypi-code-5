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

    def __init__(self, wsdl='wsdl/partner.xml', cacheDuration=0, **kwargs):
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

    def login(self, username, password, token='', is_production=False):
        lr = self._login(username, password, token, is_production)
        self._setEndpoint(lr.serverUrl, base=True)

        return lr 

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
    def _setEndpoint(self, location, base=False):
        try:
            if base:
                self._base_client.set_options(location=location)
            else:
                self._client.set_options(location=location)
        except:
            if base:
                self._base_client.wsdl.service.setlocation(location)
            else:
                self._client.wsdl.service.setlocation(location)

        self._location = location

    def _default_log_info(self):
        log_info = self._client.factory.create('LogInfo')
        log_info.category = 'All'
        log_info.level = 'Debug'
        return log_info

    def _make_log_info(self, cat, lvl):
        log_info = self._client.factory.create('LogInfo')
        log_info.category = cat
        log_info.level = lvl

        return log_info

    #TODO eval
    def _setHeaders(self, call=None):
        _base_calls = ['login', 'query_base']
        headers = {'SessionHeader': self._sessionHeader}
        if call in _base_calls:
            if self._loginScopeHeader is not None:
                headers['LoginScopeHeader'] = self._loginScopeHeader
        if call == 'runTests':
            debug_header = self.generateHeader('DebuggingHeader')
            debug_header.categories.append(self._default_log_info())
        if call == 'executeAnonymous':
            debug_header = self.generateHeader('DebuggingHeader')
            debug_header.categories.append(self._make_log_info('Db', 'DEBUG'))
            debug_header.categories.append(self._make_log_info('Workflow', 'DEBUG'))
            debug_header.categories.append(self._make_log_info('Validation', 'DEBUG'))
            debug_header.categories.append(self._make_log_info('Callout', 'DEBUG'))
            debug_header.categories.append(self._make_log_info('Apex_code', 'DEBUG'))
            debug_header.categories.append(self._make_log_info('Apex_profiling', 'DEBUG'))
            debug_header.debugLevel = 'Debugonly'
            headers['DebuggingHeader'] = debug_header
        
        self._base_client.set_options(soapheaders=headers)
        try:
            self._client.set_options(soapheaders=headers)
        except:
            pass

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
            try:
                return self._base_client.factory.create(name)
            except:
                print "Object not found"

    def create_generic_sobject(self, type=None):
        so = self.create_object('ens:sObject')
        so.type = type
        return so
 
    def query(self, query):
        self._setHeaders('query_base')
        resp = self._base_client.service.query(query)
        return resp

    def create(self, records):
        self._setHeaders('create')
        resp = self._base_client.service.create(records)
        return resp

    def upsert(self, records, external_id):
        self._setHeaders('upsert')
        resp = self._base_client.service.upsert(external_id, records)
        return resp
