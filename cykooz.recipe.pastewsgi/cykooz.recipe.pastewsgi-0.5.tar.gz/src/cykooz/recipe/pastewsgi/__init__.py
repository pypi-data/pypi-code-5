# cykooz.recipe.pastewsgi
# Copyright (C) 2014 Cykooz
import os

from zc.recipe.egg.egg import Eggs


WRAPPER_TEMPLATE = '''\
import sys
sys.path[0:0] = [
    %(syspath)s,
]
%(environ)s
%(initialization)s
from paste.deploy import loadapp
application = loadapp("config:%(config)s")
'''


class Recipe(object):
    """Buildout recipe: tranchitella.recipe.wsgi:default"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.options['eggs'] += '\nPasteDeploy'
        self.script_name = options.get('script-name', self.name)

    def install(self):
        egg = Eggs(self.buildout, self.options['recipe'], self.options)
        requirements, ws = egg.working_set()
        path = [pkg.location for pkg in ws]
        extra_paths = self.options.get('extra-paths', '')
        extra_paths = extra_paths.split()
        path.extend(extra_paths)
        environ = self.options.get('environ', '')
        initialization = self.options.get('initialization', '')
        if environ:
            environ = ["os.environ['%s'] = '%s'" % tuple(s.strip() for s in i.split('=', 1))
                       for i in environ.splitlines() if '=' in i]
            environ.insert(0, 'import os')
            environ = '\n'.join(environ)
        output = WRAPPER_TEMPLATE % dict(
            config=self.options['config-file'], environ=environ,
            initialization=initialization,
            syspath=',\n    '.join(repr(p) for p in path))
        location = self.buildout['buildout']['bin-directory']
        target = os.path.join(location, self.script_name)
        open(target, 'wt').write(output)
        os.chmod(target, 0755)
        self.options.created(target)
        return self.options.created()

    def update(self):
        self.install()
