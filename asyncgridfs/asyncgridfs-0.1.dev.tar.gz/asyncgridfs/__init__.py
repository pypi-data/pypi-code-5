# -*- coding:utf-8 -*- 
#!/usr/bin/env python
"""
    author comger@gmail.com
    async mongodb gridfs with tornado IOLoop
"""
import asyncmongo
from tornado import gen
from functools import partial
from bson.py3compat import StringIO
from bson.binary import Binary
import datetime
from bson.binary import Binary
from bson import ObjectId

chunks_coll = lambda coll: '%s.chunks' % coll
files_coll = lambda coll: '%s.files' % coll


def initcallback(callback, res, error):
    if error:raise error
    callback(res)

class GridFS(object):
    def __init__(self, client, root_collection='fs'):
        assert isinstance(client, asyncmongo.Client)
        assert isinstance(root_collection,(str,unicode))
        self.client = client
        self.root_collection = root_collection
    
    def list(self, callback=None):
        """ list all filename in gfs db """
        def func(res, error):
            if error:raise error
            callback(res['values'])

        self.client.command('distinct',files_coll(self.root_collection), key='filename', callback=func)

    def find(self, *args, **kwargs):
        coll = self.client.connection(files_coll(self.root_collection))
        func = partial(initcallback,kwargs['callback'])
        kwargs['callback'] = func
        coll.find(*args,**kwargs)

    def get(self, fid, callback=None):
        out = GridOut(self.client,self.root_collection,fid)
        out.read(callback=callback)

    def put(self, data, callback = None, **kwargs):
        grid_file = GridIn(self.client, self.root_collection, **kwargs)
        grid_file.write(data, callback = callback, **kwargs)

class GridIn(object):
    def __init__(self, client, root_collection, **kwargs):
        self.client = client
        self.root_collection = root_collection
        self._files = self.client.connection(files_coll(self.root_collection))
        self._chunks = self.client.connection(chunks_coll(self.root_collection))
        self._id = None

    def write(self, data, callback = None, **kwargs):
        self._id = ObjectId()

        _file = dict()
        _file["_id"] = self._id
        _file["length"] = len(data)
        _file["uploadDate"] = datetime.datetime.utcnow()
        _file.update(kwargs)

        def insert_files(res, error):
            chunk = {"files_id": self._id,
                    "n": 0,
                    "data": Binary(data)}

            def temp(r, error):
                pass

            self._chunks.insert(chunk, callback = temp)
            callback(self._id)

        self._files.insert(_file, callback = insert_files)


class GridOut(object):

    def __init__(self, client, root_collection, fid):
        self.client = client
        self.root_collection = root_collection
        self.fid = fid
        
    
    def get_file(self, callback):
        """　read fid's file infomation """
        self.__files_coll = self.client.connection(files_coll(self.root_collection))
        func = partial(initcallback,callback)
        self.__files_coll.find_one({"_id": self.fid}, callback=func)

    def read(self,fileobj=None, callback=None):
        """ read a file from gfs include file's infomation and data"""
        if not fileobj:
            func = partial(self.read,callback=callback)
            return self.get_file(callback=func)

        self.__chunks_coll = self.client.connection(chunks_coll(self.root_collection))
        cond = dict(files_id = self.fid)
        def surcor_callback(res,error):
            data = StringIO()
            for item in res:
                data.write(item['data'])
            
            fileobj['data'] = data.getvalue() 
            callback(fileobj)

        self.__chunks_coll.find(cond,sort=[('n',-1)],callback=surcor_callback)


