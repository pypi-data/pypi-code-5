import os
import sys
import tornado.ioloop
import logging
import time
import unittest
import asyncmongo

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from asyncgridfs import GridFS

from bson.objectid import ObjectId

class GridfsTest(unittest.TestCase):

    def setUp(self):
        super(GridfsTest, self).setUp()
        self.db = asyncmongo.Client(pool_id='test_query', host='127.0.0.1', port=27017, dbname='gfs', mincached=3)


    def test_get(self):
        fs = GridFS(self.db,'fs')

        def put_cb(_id):
            def noop_callback(response):
                print response
                logging.info(response)
                loop = tornado.ioloop.IOLoop.instance()
                # delay the stop so kill cursor has time on the ioloop to get pushed through to mongo
                loop.add_timeout(time.time() + .1, loop.stop)

            fs.get(_id,noop_callback)

        fs.put("78hlkjhg90ik75678", file_name = "a.png", contentType="image/png", 
                                    chunk_size = 3,
                                    callback = put_cb)

        #fs.list(noop_callback)

        #def find_callback(res, error):
        #    print res,error
        #    tornado.ioloop.IOLoop.instance().stop()
        #
        #fs.find({'contentType':'image/png','code_name':'test-0000-a'},callback=noop_callback)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    unittest.main()
