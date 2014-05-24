
import sys
if sys.version_info > (3,0):
    import importlib

#
# These packages contain plugins that need to be loaded
#
packages = ['coopr.opt', 'coopr.pyomo', 'coopr.os', 'coopr.pysp', 'coopr.neos', 'coopr.openopt', 'coopr.solvers', 'coopr.gdp', 'coopr.mpec', 'coopr.dae', 'coopr.bilevel']
# 
# These packages are under development, or they may be omitted in a Coopr installation
#
optional_packages = set(['coopr.neos', 'coopr.bilevel', 'coopr.mpec'])


def do_import(pname):
    if sys.version_info > (3,0):
        importlib.import_module(pname)
    else:
        __import__(pname, globals(), locals(), [], -1)


def import_packages():
    for name in packages:
        pname = name+'.plugins'
        #if pname in sys.modules:
            # This package has already been imported
            #pass
        imported = False
        if name in optional_packages:
            try:
                do_import(pname)
                imported = True
            except ImportError:
                pass
        else:
            do_import(pname)
            imported = True
        if imported:
            pkg = sys.modules[pname]
            pkg.load()
    #import coopr.core.plugin
    #coopr.core.plugin.display(verbose=True)

import_packages()

