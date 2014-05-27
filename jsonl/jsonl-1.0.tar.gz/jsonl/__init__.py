'''
jsonl:  JSON loader which overrides the default JSON module's load and loads methods.
The result is either a mutable object or immutable collections.namedtuple containing
the JSON's dictionary keys as named attributes, and the dictionary values as the
attribute's values - much like javascript !
'''

from jsonl import _jsonl as jsonl
try:
    import simplejson as json
except:
    import json

import sys

jsonl.__author__ = 'Francis Horsman'
jsonl.__version__ = '1.0'
jsonl.__email__ = 'francis.horsman@gmail.com'
jsonl.__doc__ = ''.join([json.__doc__, __doc__])
jsonl.__name__ = __name__
jsonl.__package__ = __name__
jsonl.__path__ = __path__

sys.modules[__name__] = jsonl
