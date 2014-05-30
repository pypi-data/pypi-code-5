from collections import namedtuple
import copy
import imp
import traceback
from types import TupleType, BuiltinFunctionType, BuiltinMethodType

__js = imp.load_module('__js', *imp.find_module('simplejson'))

_JSONL = 'JSONL'
__version__ = '1.3'
__author__ = 'Francis Horsman'
__email__ = 'francis.horsman@gmail.com'

class _jsonl(object):
    OBJECT_NAME = '_'.join([_JSONL, 'v1d3'])

_jsonl = _jsonl()

for name in dir(__js):
    setattr(_jsonl, name, getattr(__js, name))

__cls = type(_jsonl.OBJECT_NAME, (object,), {})()

def __loads(json_data, *args, **kwargs):
    '''
    @see json.loads
    @param kwargs['__mutable__']: True = mutable generic object used, otherwise = immutable collections.namedTuple used.
    '''
    def getAttributes(d):
        attributes, values = zip(*sorted(d.items()))
        return namedtuple(_jsonl.OBJECT_NAME, list(attributes))(*values)
    createImmutable = getAttributes
    def createMutable(d):
        cls = copy.deepcopy(__cls)
        for k, v in d.items():
            setattr(cls, k, v)
        return cls
    createCls = createMutable if kwargs.pop('__mutable__', True) else createImmutable
    def lamb(x):
        return createCls(x)
#        kwargs['object_hook'] = lambda x: createCls(x)
    kwargs['object_hook'] = lamb
    return __js.loads(json_data, *args, **kwargs)

def __serializeMutable(obj):
    new_obj = {}
    for name in dir(obj):
        if not name.startswith('_'):
            value = getattr(obj, name)
            if __cls.__class__ == value.__class__:
                value = __serializeMutable(value)
            elif isinstance(value, list):
                result = []
                for i in iter(value):
                    if __cls.__class__ == i.__class__:
                        result.append(__serializeMutable(i))
                    else:
                        result.append(i)
                value = result
            new_obj[name] = value
    return new_obj

def __serializeImmutable(obj):
    new_obj = {}
    ignoreCount = (type(obj.count) in [BuiltinFunctionType, BuiltinMethodType])
    ignoreIndex = (type(obj.index) in [BuiltinFunctionType, BuiltinMethodType])
    for name in dir(obj):
        if not name.startswith('_'):
            if (name == 'count' and ignoreCount):
                continue
            elif (name == 'index' and ignoreIndex):
                continue
            value = getattr(obj, name)
            if __cls.__class__ == value.__class__:
                value = __serializeMutable(value)
            new_obj[name] = value
    return new_obj

def __dumps(obj, *args, **kwargs):
    '''
    @see json.dumps
    '''
    if isinstance(obj, basestring):
        return __js.dumps(obj)
    new_obj = {}
    if __cls.__class__ == obj.__class__:
        new_obj = __serializeMutable(obj)
    elif isinstance(obj, TupleType) and obj.__doc__.startswith(_jsonl.OBJECT_NAME):
        new_obj = __serializeImmutable(obj)
    else:
        new_obj = obj
    return __js.dumps(new_obj, *args, **kwargs)

def __load(fp, *args, **kwargs):
    if isinstance(fp, basestring):
        return _jsonl.loads(open(fp, 'rb').read().strip(), *args, **kwargs)
    return _jsonl.loads(fp.read().strip(), *args, **kwargs)

def __dump(obj, fp, *args, **kwargs):
    if isinstance(fp, basestring):
        with open(fp, 'wb') as f:
            return f.write(_jsonl.dumps(obj, *args, **kwargs))
    return fp.write(_jsonl.dumps(obj, *args, **kwargs))

def __compare(a, b, force=False):
    '''
    @summary: Comparator method compares persisted values also.
    @param: force: True - force type-coercion.
    @param a: basestring, Any object returned from jsonl.loads()
    @param b: basestring, Any object returned from jsonl.loads()
    '''
    def compare(c, d):
        if type(c) != type(d):    return False
        if isinstance(c, dict):
            #    dicts are order-independent
            attributesC, valuesC = zip(*sorted(c.items()))
            attributesD, valuesD = zip(*sorted(d.items()))
            if not compare(attributesC, attributesD):    return False
            if not compare(valuesC, valuesD):    return False
        elif isinstance(c, (list, tuple)):
            #    lists are order-dependent
            if len(c) != len(d):  return False
            for i in xrange(len(c)):
                if not compare(c[i], d[i]):return False
        return c == d
    aClassName = a.__class__.__name__
    customClassName = __cls.__class__.__name__
    bClassName = b.__class__.__name__
    aIsString = isinstance(a, basestring)
    bIsString = isinstance(b, basestring)
    aIsExactCustomClass = (aClassName == customClassName)
    bIsExactCustomClass = (bClassName == customClassName)
    aIsCustomClass = (aClassName == customClassName)
    bIsCustomClass = (bClassName == customClassName)
    compatable = True
    if aIsCustomClass or bIsCustomClass:
        #    Are our custom classes compatable?
        compatable = __areClassesCompatable(a, b, force)
    if isinstance(a, basestring) and bIsString:
        #    Both are string JSON(l) dumps so compare the actual data:
        return compare(__js.loads(a), __js.loads(b))
    elif aIsExactCustomClass or bIsExactCustomClass:
        if aIsExactCustomClass and bIsExactCustomClass \
            or (aIsCustomClass and bIsCustomClass and compatable):
            #    We have a custom jsonl class as both
            return __compare(__dumps(a), __dumps(b))
        elif aIsExactCustomClass and bIsString:
            #    One custom jsonl class and a string
            return __compare(__dumps(a), b)
        elif bIsExactCustomClass and aIsString:
            #    One custom jsonl class and a string
            return __compare(a, __dumps(b))
    return compare(a, b)

def __areClassesCompatable(a, b, force):
    '''
    @note: At least one of a or b is a custom class.
    Both classes must be compatable with 'this' version.
    '''
    if force:   return True
    aClassName = a.__class__.__name__
    customClassName = __cls.__class__.__name__
    bClassName = b.__class__.__name__
    if aClassName == bClassName:  return True
    aIsCustomClass = (aClassName == customClassName)
    bIsCustomClass = (bClassName == customClassName)
    if (aIsCustomClass and not bIsCustomClass) or\
        (bIsCustomClass and not aIsCustomClass):
        return True
    #    Both are guaranteed to be custom classes at this point.
    tokensCurrent = _jsonl.OBJECT_NAME.split('_')
    tokensA = a.__class__.__name__.split('_')
    tokensB = b.__class__.__name__.split('_')
    versionCurrent = tokensCurrent[1]
    versionA = tokensA[1]
    versionB = tokensB[1]
    #    Check the classes dependency graphs for (in)compatibility
    return __checkCompatibility(versionA, versionCurrent) and __checkCompatibility(versionB, versionCurrent)

def __checkCompatibility(a, versionCurrent):
    '''
    @note: 'a'!=versionCurrent. If 'a' > 'versionCurrent' then False,
    if 'a' not in matrix-tree then assume False.
    @todo: Refactor this out into a separate class.
    '''
    #    Is a compatible with versionCurrent or vici versa?
    try:
        splitter = 'd'
        version = 'v'
        vString = a[1:]
        vcString = versionCurrent[1:]
        tokensA = vString.split(splitter)
        if a[0] != version: raise JsonlParseError(a, versionCurrent)
        if versionCurrent[0] != version: raise JsonlParseError(a, versionCurrent)
        tokensV = vcString.split(splitter)
        def greaterThan(c, d):
            if c[0] > d[0]: return True
            if d[0] > c[0]: return False
            if c[1] > d[1]: return True
            return False
        def find(a, versionCurrent, matrix):
            '''
            @note: 'a' is guaranteed to be < versionCurrent
            '''
            if a not in matrix.keys():  return False
            if versionCurrent not in matrix.keys():
                raise JsonlParseError(a, versionCurrent)
            def get(a, node, visited):
                yes = node.get('yes', [])
                no = node.get('no', [])
                if a in no:
                    raise No()
                elif a in yes:
                    raise Yes()
                #    Recurse - explicit 'yes' is required:
                for i in yes:
                    #    Check for circular dependency:
                    if i in visited:
                        raise Circ(''.join([version, i]))
                    if i in matrix:
                        get(a, matrix[i], set(list(visited) + [i]))
            try:
                get(a, matrix[versionCurrent], set([]))
            except Yes:
                return True
            except No:
                return False
            except Circ:
                raise
            #    Explicit Failure if we can't find it!
            return False
        #    Check a>v:
        if greaterThan(tokensA, tokensV):   return False
        if not find(vString, vcString, __COMPAT_MATRIX): return False
        return True
    except JsonlParseError as e:
        e.traceback = traceback.format_exc()
    except Exception as e:
        raise JsonlParseError(a, versionCurrent, e, traceback.format_exc())

class Yes(Exception):   pass
class No(Exception):    pass
class Circ(Exception):
    def __str__(self):
        return 'Circular dependency: %s' % self.message

class JsonlParseError(Exception):
    def __init__(self, a, versionCurrent, e=None, trace=None):
        self.traceback = trace
        self.version = a
        self.versionCurrent = versionCurrent
        super(JsonlParseError, self).__init__(e)
    def __str__(self):
        s = [str(self.args[0]), 'in', self.version]
        if self.traceback != None:
            s.append('\n')
            s.append(self.traceback)
        return ' '.join(s)

#    Example configuration (nothing prior to v1.0 is compatible with >= v1.0:
__COMPAT_MATRIX = {'1d3':{'yes':['1d2'], 'no':['0d9', '0d8']},
                   '1d2':{'no':['0d9'], 'yes':['1d0']},
                   '1d0':{'no':['0d9']},
                   '0d9':{},
                   }

setattr(_jsonl, 'load', __load)
setattr(_jsonl, 'loads', __loads)
setattr(_jsonl, 'dump', __dump)
setattr(_jsonl, 'dumps', __dumps)
setattr(_jsonl, 'isEqual', __compare)
setattr(_jsonl, '__version__', __version__)
setattr(_jsonl, '__author__', __author__)
setattr(_jsonl, '__email__', __email__)

#    Check the version string:
__tokens = _jsonl.OBJECT_NAME.split('_')
if __tokens[0] != _JSONL:
    raise Exception('JSONL version incorrectly formatted: "%s"' % _jsonl.OBJECT_NAME)
elif __tokens[1][1:] not in __COMPAT_MATRIX.keys():
    raise Exception('Current JSONL version not in compatibility matrix: "%s"' % _jsonl.OBJECT_NAME)
#    TODO:    Perform static circular dependency check and logic check of __COMPAT_MATRIX.

if __name__ == '__main__':
    a = {'a':['aa'], 'b':{'c':['cc']}, 'd':{'e':[1, 2, 3]}}
    js = _jsonl

    for m in [False, True]:
        aa = js.dumps(a)
        a_ = js.loads(aa, __mutable__=m)

        print type(a), a
        print type(aa), aa
        print type(a_), a_
        print type(a_.a), a_.a
        print type(a_.b), a_.b
        print type(a_.b.c), a_.b.c
        print type(a_.d), a_.d

        aaa = js.dumps(a_)
        print type(aaa), aaa,
        aaaa = js.loads(aaa)
        print type(aaaa), aaaa, 'done'

