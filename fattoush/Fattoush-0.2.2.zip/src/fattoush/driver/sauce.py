# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
Interface between Sacue Labs and lettuce driver 
"""
from abc import ABCMeta, abstractmethod
import base64
import hmac
import json
import urllib2


class SauceInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_session_configuration(self, **conf):
        pass

    @abstractmethod
    def fail_session(self):
        pass

    @abstractmethod
    def set_session_configuration(self, **conf):
        pass

    @abstractmethod
    def add_file_to_storage(self, binary_string, server_path,
                            overwrite=False):
        return "sauce:storage:NAME"


class AbstractSauceBase(SauceInterface):

    __metaclass__ = ABCMeta

    session_text_template = "SauceOnDemandSessionID={0} job-name={1}"
    public_url_template = "https://saucelabs.com/jobs/{0}?auth={1}"

    user = "saucelabs_username"
    key = "saucelabs_api_key"

    default_headers = {}

    def __init__(self, config, browser):
        """
        :param config: fattoush.config.FattoushConfig
        :param browser: fattoush.driver.driver.Driver
        """

        # Bind copy of class defaults to instance
        self.default_headers = self.default_headers.copy()

        self.wd_hub = config.command_executor
        self.session_name = config.name

        self.browser = browser
        self.job_id = browser.session_id

        self.combined_key = "{0}:{1}".format(self.user, self.key)
        self.token = hmac.new(self.combined_key,
                              self.job_id).hexdigest()

        self.public_url = self.public_url_template.format(self.job_id,
                                                          self.token)

    @abstractmethod
    def request(self, endpoint, method='GET', body=None,
                extra_headers=None):
        return "Response"

    def set_session_configuration(self, **conf):
        body_content = json.dumps(conf)
        endpoint = '/rest/v1/{0}/jobs/{1}'.format(self.user,
                                                  self.job_id)

        self.request(endpoint, 'PUT', body_content)

    def fail_session(self):
        self.set_session_configuration(passed=False)

    def add_file_to_storage(self, binary_string, server_path,
                            overwrite=False):
        endpoint = '/rest/v1/storage/%s/%s?overwrite=%s' % (
            self.user.strip('/'),
            server_path.strip('/'),
            ('false', 'true')[overwrite])
        ret = self.request(endpoint=endpoint, method='POST',
                           body=binary_string)
        return "sauce-storage:%s" % server_path, ret

    @property
    def scenario_details(self):
        return {
            "user": self.user,
            "job_id": self.job_id,
            "session_name": self.session_name,
            "key": self.combined_key,
            "token": self.token,
            "public_url": self.public_url,
        }


class Local(AbstractSauceBase):
    """
    Local Interface for testing 
    """
    def request(self, endpoint, method='GET', body=None,
                extra_headers=None):
        print ("Would [{0}]{1} with body of {2} (extra-headers={3})"
               .format(method, endpoint, body, extra_headers))

    def __init__(self, config, browser):
        super(Local, self).__init__(config, browser)


class Sauce(AbstractSauceBase):
    """
    Connect to real Saucelabs infrastructure
    """
    def __init__(self, config, browser):

        self.user = config.server["user"]
        self.key = config.server["key"]

        self._url_ = "http://saucelabs.com/{0}"

        super(Sauce, self).__init__(config, browser)

        self.session_text = self.session_text_template.format(
            self.job_id, self.session_name)

        self.b64_key = base64.encodestring(self.combined_key)[:-1]

        self.default_headers["Authorization"] = "Basic {0}".format(
            self.b64_key)

        print self.session_text
        print self.public_url

    def _url(self, endpoint):
        return self._url_.format(endpoint.lstrip('/'))

    def _headers(self, extra_headers):
        headers = self.default_headers.copy()
        if extra_headers is not None:
            headers.update(extra_headers)

        return headers

    def request(self, endpoint, method='GET', body=None,
                extra_headers=None):
        request = urllib2.Request(url=self._url(endpoint),
                                  data=body,
                                  headers=self._headers(extra_headers))
        request.get_method = lambda: method

        return urllib2.urlopen(request)
        