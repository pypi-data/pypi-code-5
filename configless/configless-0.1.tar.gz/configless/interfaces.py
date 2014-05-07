# -*- coding:utf-8 -*-
from zope.interface import (
    Interface,
    Attribute
)

class IConfigurator(Interface):
    def include(module_or_function):
        pass

    def add_plugin(name, plugin, iface=None, categoryname=None):
        pass

    def activate_plugin(name, *args, **kwargs):
        pass

class IPlugin(Interface):
    def create_from_setting(setting): #classmethod
        pass


