import imp
from collections import namedtuple

try:
    __js = imp.load_module('__js', *imp.find_module('simplejson'))
except:
    __js = imp.load_module('__js', *imp.find_module('json'))

class _jsonl(object):
    OBJECT_NAME = 'JSONObject'

_jsonl = _jsonl()

for name in dir(__js):
    setattr(_jsonl, name, getattr(__js, name))

def loads(json_data, *args, **kwargs):
    '''
    @see json.loads
    @param kwargs['__mutable__']: True = mutable object used, otherwise = immutable collections.namedTuple used.
    '''
    createImmutable = lambda d: namedtuple(_jsonl.OBJECT_NAME, d.keys())(*d.values())
    def createMutable(d):
        cls = type(_jsonl.OBJECT_NAME, (object,), {})()
        for k, v in d.items():
            setattr(cls, k, v)
        return cls
    createCls = createMutable if kwargs.pop('__mutable__', True) else createImmutable
    kwargs['object_hook'] = lambda d: createCls(d)
    return __js.loads(json_data, *args, **kwargs)

def load(fp, *args, **kwargs):
    return _jsonl.loads(open(fp, 'rb').read().strip(), *args, **kwargs)

setattr(_jsonl, 'load', load)
setattr(_jsonl, 'loads', loads)
