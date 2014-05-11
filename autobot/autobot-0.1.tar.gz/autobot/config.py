#!/usr/bin/env python

"""
tools for interpolating buildbot configuration
"""

import argparse
import sys
from projects import factories
from ConfigParser import RawConfigParser


class BuildbotIniConfig(object):
    """
    class for getting a (for now, autobot-specific)
    buildbot configuration from an .ini file
    """

    def __init__(self, filename):

        # read the .ini file
        self.parser = RawConfigParser()
        self.parser.read(filename)

        # get global information
        master = ':master:'
        self.master = self.section_dict(master)
        for port, default in ('slaveport', 9010), ('htmlport', 8010), ('publichtmlport', 8011):
            self.master[port] = int(self.master.get(port) or default)
        channels = self.master.get('channels', '').strip()
        if channels:
            self.master['channels'] = channels.split()
        else:
            self.master['channels'] = []

        # get section information
        self.slaves = {}
        self.args = {}
        for section in self.parser.sections():

            # ignore master section -- we've already dealt with that
            if section == master:
                continue

            # get slave
            if section.startswith('slave:'):
                name = section.split('slave:', 1)[-1]
                slave_dict = self.master.copy()
                slave_dict.update(self.section_dict(section))
                assert 'password' in slave_dict, 'Slave %s: must provide a password' % name

                # get factories
                _factories = slave_dict.get('factories', '')
                _factories = _factories.split()
                if _factories == ['']:
                    _factories = []
                if _factories == ['*']:
                    _factories = factories.keys()

                # get platform information
                platform = {}
                for key in ('os',):
                    if key in slave_dict:
                        platform[key] = slave_dict.pop(key)
                    else:
                        platform[key] = None

                # put it together coherently
                self.slaves[name] = {'password': slave_dict['password'],
                                     'factories': _factories,
                                     'platform': platform }
                continue

            # get factories
            self.args[section] = self.section_dict(section)

        # TODO: schedulers + sources ([source:<factory>])

    def section_dict(self, section):
        """
        returns the section as a dict
        """
        if section in self.parser.sections():
            return dict(self.parser.items(section))
        else:
            return {}

def main(args=sys.argv[1:]):
    """parse the configuration, mostly for testing purposes"""

    parser = argparse.ArgumentParser(description="parse autobot .ini configuration")
    parser.add_argument('ini', help=".ini file to try to parse")
    config = BuildbotIniConfig(parser.ini)

if __name__ == '__main__':
    main()
