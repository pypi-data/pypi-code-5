# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
Functions for putting together sauce configuration,
be it from environmental variables or from a JSON string.
"""
import json

from os import path
from lettuce import Runner
from selenium.webdriver import DesiredCapabilities


class FattoushConfig(object):

    def _augment_xunit_filename(self):
        index = self.index
        xunit_file = self.run_args['xunit_filename']

        if xunit_file is None:
            return

        if '.' in path.basename(xunit_file):
            prefix, suffix = path.splitext(xunit_file)
            xunit_file = '{0}_{1}.{2}'.format(prefix, index, suffix)
        else:
            xunit_file = '{0}_{1}'.format(xunit_file, index)
        self.run_args['xunit_filename'] = xunit_file

    def _augment_server(self):
        if self.server is None:
            self.server = {}
        server = self.server
        if "host" not in server:
            server[u"host"] = ("127.0.0.1" if "user" not in server
                               else "ondemand.saucelabs.com")
        if "port" not in server:
            server[u"port"] = ("4444" if "user" not in server
                               else "80")
        if "url" in server and not server["url"]:
            del server["url"]

    def run(self):
        try:
            return Runner(**self.run_args).run()
        except BaseException:
            print "Lettuce raised the following exception:"
            raise

    def _augment_browser(self):
        """
        All parts of the browser config must be a string except for the
        description, which can hold any format.
        """

        def to_string(obj):
            try:
                if isinstance(obj, unicode):
                    return obj
                elif isinstance(obj, list):
                    return ''.join(obj)
            except TypeError:
                return json.dumps(obj)

        if "description" in self.browser:
            self.browser["description"] = to_string(
                self.browser["description"])

    def __init__(self, index, browser, server, lettuce):
        """
        :param index: int
        :param browser: dict
        :param server: dict
        :param lettuce: dict
        """
        self.index = index
        self.server = server
        self.browser = browser.copy()
        self.run_args = lettuce

        self._augment_xunit_filename()
        self._augment_server()

        self._augment_browser()
        self.name = ";".join(('='.join(item) for item in
                              sorted(self.browser.items())
                              if item[0] != "description"))

    @property
    def command_executor(self):
        host = self.server["host"].rstrip('/')

        try:
            protocol, host = host.split("://")
        except ValueError:
            protocol = 'http'

        try:
            host, url_path = host.split(":")
        except ValueError:
            port = self.server["port"]
        else:
            split_path = url_path.split("/")
            port = split_path[0]
            split_path[0] = host
            host = '/'.join(split_path)

        split_path = host.split('/')
        host, split_path = split_path[0], split_path[1:]

        endpoint = "/".join(split_path) if split_path else "wd/hub"

        if "user" in self.server and "key" in self.server:
            return ('{protocol}://{user}:{key}@{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             user=self.server["user"],
                             key=self.server["key"],
                             host=host,
                             port=port,
                             endpoint=endpoint)

        elif "user" in self.server:
            return ('{protocol}://{user}@{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             user=self.server["user"],
                             host=host,
                             port=port,
                             endpoint=endpoint)
        else:
            return ('{protocol}://{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             host=host,
                             port=port,
                             endpoint=endpoint)

    @property
    def browser_lookup(self):
        return {
            "android": DesiredCapabilities.ANDROID,
            "googlechrome": DesiredCapabilities.CHROME,
            "firefox": DesiredCapabilities.FIREFOX,
            "phantom": DesiredCapabilities.PHANTOMJS,
            "htmlunit": DesiredCapabilities.HTMLUNIT,
            "iexploreproxy": DesiredCapabilities.INTERNETEXPLORER,
            "iphone": DesiredCapabilities.IPHONE
        }

    def desired_capabilities(self, scenario):
        """
        :param scenario: Scenario
        """

        desired = self.browser.copy()
        browser = desired.pop("browser")
        desired["name"] = scenario.name

        try:
            capabilities = self.browser_lookup[browser]
        except KeyError:
            capabilities = DesiredCapabilities.CHROME

        capabilities.update(desired)
        return capabilities
