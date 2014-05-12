# pylint: disable-msg=W0622
"""cubicweb-codenaf application packaging information"""

modname = 'codenaf'
distname = 'cubicweb-codenaf'

numversion = (0, 1, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = 'the NAF keyword hierarchy for the CubicWeb framework'
long_desc = '''\
This cube provides a classification implementing the Code NAF from the french
national institute of statistics (INSEE).

See http://fr.wikipedia.org/wiki/Code_NAF for more information about the NAF
classification scheme.
'''

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]


__depends_cubes__ = {'keyword': None,}
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, modname),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, modname, 'bin'),
         [join('bin', fname) for fname in listdir('bin')]],
        [join(CUBES_DIR, modname, 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, modname, 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, modname, 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass
