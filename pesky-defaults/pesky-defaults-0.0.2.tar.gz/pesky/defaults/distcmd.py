# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import os, json
from setuptools import Command
from distutils import log
from pkg_resources import safe_name, to_filename


class pesky_default(Command):

    # Brief (40-50 characters) description of the command
    description = "manipulate pesky defaults"

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [
        ('command=', None, "perform the specified COMMAND (get, set, clear, flush, list)"),
        ('key=', None, "manipulate default named KEY"),
        ('value=', None, "set default to the specified VALUE"),
        ]

    def initialize_options(self):
        self.egg_name = None
        self.egg_base = None
        self.defaults_path = None
        self.command = None
        self.key = None
        self.value = None

    def finalize_options(self):
        self.egg_name = safe_name(self.distribution.get_name())
        log.debug("egg_name = " + self.egg_name)
        if self.egg_base is None:
            dirs = self.distribution.package_dir
            self.egg_base = (dirs or {}).get('',os.curdir)
        log.debug("egg_base = " + self.egg_base)
        self.ensure_dirname('egg_base')
        self.egg_info = to_filename(self.egg_name) + '.egg-info'
        if self.egg_base != os.curdir:
            self.egg_info = os.path.join(self.egg_base, self.egg_info)
        log.debug("egg_info = " + self.egg_info)
        self.defaults_path = os.path.join(self.egg_info, "pesky_defaults.json")

    def read_defaults(self):
        if not os.access(self.defaults_path, os.F_OK):
            return dict()
        with open(self.defaults_path, 'r') as f:
            return json.loads(f.read())

    def write_defaults(self, defaults):
        log.debug("writing pesky defaults to %s", self.defaults_path)
        if not self.dry_run:
            with open(self.defaults_path, 'w') as f:
                f.write(json.dumps(defaults))

    def run(self):
        if self.command is None:
            log.info("no command specified")
            return 0
        command = self.command.lower()
        defaults = self.read_defaults()
        # commands which don't require a key
        if command == 'list':
            for key,value in sorted(defaults.items()):
                print "%s: %s" % (key, str(value))
            return 0
        if command == 'flush':
            log.debug("flushing all defaults")
            self.write_defaults(dict())
            return 0
        # commands which require a key
        if self.key is None:
            log.info("no key specified")
            return 0
        if command == 'get':
            if self.key in defaults:
                print defaults[self.key]
            return 0
        if command == 'set':
            log.debug("setting %s = '%s'" % (self.key, self.value))
            defaults[self.key] = self.value
            self.write_defaults(defaults)
            return 0
        if command == 'clear':
            log.debug("clearing %s" % self.key)
            if self.key in defaults:
                del defaults[self.key]
                self.write_defaults(defaults)
            return 0
        log.info("unknown command %s" % self.command)
        return 1
