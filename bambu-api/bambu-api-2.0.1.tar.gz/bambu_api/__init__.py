"""
Quickly expose your models to a JSON or XML API, authenticated via HTTP or
OAuth.
"""

__version__ = '2.0.1'

from bambu_api.options import *
from bambu_api.sites import APISite
from bambu_api.exceptions import APIException
from bambu_api.decorators import argument, returns, named
from django.conf import settings
from datetime import datetime

default_app_config = 'bambu_api.apps.APIConfig'
site = APISite()

def autodiscover():
    """
    Works like ``django.contrib.admin.autodiscover``, running thorugh each of the packages within a
    project's ``INSTALLED_APPS`` setting, to find instances of an ``api`` module which might contain
    calls to ``bambu_api.site.register``.

    Unlike ``django.contrib.admin.autodiscover``, you do not need to call this function manually.
    """

    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    from copy import copy, deepcopy
    from bambu_api.endpoints import *

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)

        try:
            before_import_registry = copy(site._registry)
            import_module('%s.api' % app)
        except:
            site._registry = before_import_registry
            if module_has_submodule(mod, 'api'):
                raise
