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
from bson.objectid import ObjectId

DEFAULT_CHUNK_SIZE = 255 * 1024
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
        grid_file.close()
        callback(grid_file._file['_id'])
    
    def delete(self, fid, callback=None):
        def next_func(res,error):
            if error:raise error
            c_coll = self.client.connection(chunks_coll(self.root_collection))
            c_coll.remove(spec_or_id=fid,callback=callback)
        
        f_coll = self.client.connection(files_coll(self.root_collection))
        c_coll.remove(spec_or_id=fid,callback=next_func)

class GridIn(object):
    def __init__(self, client, root_collection, **kwargs):
        self.client = client
        self.root_collection = root_collection
        self._files = self.client.connection(files_coll(self.root_collection))
        self._chunks = self.client.connection(chunks_coll(self.root_collection))

        # Handle alternative naming
        if "content_type" in kwargs:
            kwargs["contentType"] = kwargs.pop("content_type")
        if "chunk_size" in kwargs:
            kwargs["chunkSize"] = kwargs.pop("chunk_size")

        # Defaults
        kwargs["_id"] = kwargs.get("_id", ObjectId())
        kwargs["chunkSize"] = kwargs.get("chunkSize", DEFAULT_CHUNK_SIZE)

        self._file = kwargs
        self._chunk_number = 0
        self._position = 0
        self._buffer = StringIO()

    def __flush_data(self, data):

        def no_check(*arg, **kwargs):
            pass

        chunk = {"files_id": self._file['_id'],
                "n": self._chunk_number,
                "data": Binary(data)}

        self._chunks.insert(chunk, callback = no_check)
        self._chunk_number += 1
        self._position += len(data)

    def __flush_buffer(self):
        self.__flush_data(self._buffer.getvalue())
        self._buffer.close()
        self._buffer = StringIO()

    def write(self, data, callback = None, **kwargs):
        try:
            read = data.read
        except AttributeError:
            read = StringIO(data).read

        if self._buffer.tell() > 0:
            space = self.chunk_size = self._buffer.tell()
            if space:
                to_write = read(space)
                self._buffer.write(to_write)
                if len(to_write) < space:
                    return # EOF
            self.__flush_buffer()

        to_write = read(self._file['chunkSize'])
        while to_write and len(to_write) == self._file['chunkSize']:
            self.__flush_data(to_write)
            to_write = read(self._file['chunkSize'])
        self._buffer.write(to_write)


    def __flush(self):
        self.__flush_buffer()

        def no_check(*arg, **kwargs):
            pass

        def cb_md5(*arg, **kwargs):
            try:
                self._file['md5'] = arg[0]['md5']
            except:
                pass
            self._file["uploadDate"] = datetime.datetime.utcnow()
            self._files.insert(self._file, callback = no_check)

        self.client.command('filemd5', self._file['_id'], root=self.root_collection, callback=cb_md5)

    def close(self):
        self.__flush()


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

