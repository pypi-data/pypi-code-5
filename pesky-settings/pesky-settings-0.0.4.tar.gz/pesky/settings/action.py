# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

from pesky.settings import Settings, ConfigureError

NOACTION = 'no action'

class ActionBase(object):
    """
    """
    def __init__(self):
        self.children = dict()

    def _init(self, settings, options, actions):
        for option in options:
            settings.add(option)
        for action in actions:
            if not isinstance(action, Action):
                raise TypeError("invalid action %s" % str(action))
            if action.name in self.children:
                raise KeyError("action %s already exists" % action.name)
            self.children[action.name] = action
            childsettings = settings.add_subcommand(action.name, action.usage, action.description)
            action._init(childsettings, action.options, action.actions)

class ActionMap(ActionBase):
    """
    """
    def __init__(self, usage, version, description, section=None, appname=None, confbase='/etc/', options=None, actions=None):
        ActionBase.__init__(self)
        self.settings = Settings(usage, version, description, section=section, appname=appname, confbase=confbase)
        if options is None:
            self.options = list()
        else:
            self.options = options
        if actions is None:
            self.actions = list()
        else:
            self.actions = actions
        self.callback = None
        self._init(self.settings, self.options, self.actions)

    def parse(self, *args, **kwargs):
        ns = self.settings.parse(*args, **kwargs)
        action = self
        name = ns.pop_stack()
        while name is not None:
            action = action.children[name]
            name = ns.pop_stack()
        callback = action.callback
        if callback is None:
            raise RuntimeError("no callback specified")
        if callback is NOACTION:
            raise ConfigureError("no action specified.  see --help for usage.")
        return callback(ns)

class Action(ActionBase):
    """
    """
    def __init__(self, name, callback=None, usage=None, description=None, options=None, actions=None):
        ActionBase.__init__(self)
        self.name = name
        self.callback = callback
        self.usage = usage
        self.description = description
        if options is None:
            self.options = list()
        else:
            self.options = options
        if actions is None:
            self.actions = list()
        else:
            self.actions = actions
