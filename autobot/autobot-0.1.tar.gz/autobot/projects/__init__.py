"""
projects that need some CI love
"""

import imp
import inspect
import os
import sys
from buildbot.process.factory import BuildFactory

__all__ = ['factories', 'descriptions', 'here', 'args']

# available factories::
# import these automagically; requires non-zipped eggs
factories = {}    # factory classes
descriptions = {} # their descriptions
args = {}         # their arguments
here = os.path.dirname(os.path.abspath(__file__))
packages = [os.path.join(here, path)
            for path in os.listdir(here)
            if os.path.isdir(os.path.join(here, path))]
packages = [os.path.basename(package) for package in packages
            if os.path.exists(os.path.join(package, '__init__.py'))]
modules = [os.path.splitext(module)[0]
           for module in os.listdir(here)
           if module.endswith('.py') and not module.startswith('_')]
packages.extend(modules)

# load the packages
for package in packages:
    try:
        module = imp.load_package('autobot.projects.'+package, imp.find_module(package, [here])[1])
    except Exception, e:
        print >> sys.stderr, "Could not import autobot.projects.%s : %s" % (package, e)
        continue
    for attr in dir(module):
        try:
            _obj = getattr(module, attr)
            if issubclass(_obj, BuildFactory) and _obj.__module__.startswith('autobot.projects.'):
                factories[package] = _obj
                descriptions[package] = (getattr(_obj, '__doc__', attr) or attr).strip()
                args[package] = inspect.getargspec(_obj.__init__).args[1:] # not self
        except TypeError:
            continue

