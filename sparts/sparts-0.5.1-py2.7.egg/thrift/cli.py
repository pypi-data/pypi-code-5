# Copyright (c) 2014, Facebook, Inc.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from argparse import ArgumentParser
from sparts.thrift.client import ThriftClient
from sparts.thrift.compiler import CompileContext

import logging
import sys

class CLI(object):
    def execFromArgs(self):
        ap = ArgumentParser()
        ap.add_argument('thrift_file')
        ap.add_argument('--service')
        ap.add_argument('method')
        ap.add_argument('args', nargs='*')
        
        ap.add_argument('--port', type=int)
        ap.add_argument('--host')
        ap.add_argument('--level', default='DEBUG')

        ns = ap.parse_args()

        logging.basicConfig(stream=sys.stderr, level=ns.level)

        ctx = CompileContext()
        module = ctx.importThrift(ns.thrift_file)

        services = self.findServices(module)
        if ns.service:
            service = services[ns.service.lower()]
        elif len(services) == 1:
            service = services.values()[0]
        else:
            raise Exception("File exports multiple sercies: %s",
                            services.keys())
        print "Using", service

        client = ThriftClient(module=service, host=ns.host, port=ns.port)

        args = []
        for arg in ns.args:
            try:
                args.append(eval(arg))
            except NameError:
                args.append(arg)

        print getattr(client, ns.method)(*args)
        

    def findServices(self, module):
        result = {}
        for k in dir(module):
            v = getattr(module, k)
            if hasattr(v, 'Iface') and hasattr(v, 'Processor'):
                result[k.lower()] = v
        print "found:", result
        return result

if __name__ == '__main__':
    CLI().execFromArgs()
