# -*- coding: utf-8 -*-
import re 
import memcache
import pickle
import os
import itertools

class Locations(object):
    memcacheHost = '127.0.0.1:11211'
    isInitialized = None
    collectionSourceFile = 'locations.db'
    collectionName = 'locationExtractor_cities'
    collection = None

    @classmethod
    def init(cls):
        try:
            cls.mcclient = memcache.Client([cls.memcacheHost], debug=0)
            cls.collection = cls.cache_retrieve(cls.collectionName)
            if not cls.collection:
                cls.collection = cls.loadFromSource()
                cls.cache_store(cls.collectionName, cls.collection)
        except:
            cls.collection = cls.loadFromSource()

        cls.isInitialized = True

    @classmethod
    def cache_store(cls, key, value, chunksize=950000):
      serialized = pickle.dumps(value, 2)
      values = {}
      for i in xrange(0, len(serialized), chunksize):
        values['%s.%s' % (key, i//chunksize)] = serialized[i : i+chunksize]
      cls.mcclient.set_multi(values)
    
    @classmethod
    def cache_retrieve(cls, key):
        result = cls.mcclient.get_multi(['%s.%s' % (key, i) for i in xrange(32)])
        serialized = ''.join([v for v in result.values() if v is not None])
        if serialized:
            return pickle.loads(serialized)
        else:
            return None

    @classmethod
    def loadFromSource(cls):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path) + '/'
        with open(dir_path + '/' + cls.collectionSourceFile,"rb") as f:
            cities = pickle.load(f)
        return cities

    @classmethod
    def detect(cls, haystack):
        if not cls.isInitialized:
            cls.init()
        
        tokens = re.compile("[ `'?.;,-/]").split(haystack.lower())
        """ Firstly checking phrases in db. Because for example:New York 
        if it searches tokens (New - York) it will found GB result. (Great Britain 
        have a city which name is York)
        """
        possibleCombines = list(itertools.combinations(tokens,2))
        for combine in possibleCombines:
            phrase = " ".join(combine) 
            try:
                return {
                    "code": cls.collection[phrase].upper(),
                    "city": phrase
                }
            except:
                pass

        for token in tokens:
            try:
                return {
                    "code": cls.collection[token].upper(),
                    "city": token
                }
            except:
                pass
 
        
        
