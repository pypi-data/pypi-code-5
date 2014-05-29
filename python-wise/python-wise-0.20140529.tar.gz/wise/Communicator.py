# -*- mode: python; coding: utf-8 -*-

from threading import Thread, Event
from tornado import web, ioloop, httpserver
from commodity import path

from .ObjectAdapter import ObjectAdapter
from .Exceptions import AlreadyRegisteredException
from .StaticFSApplication import StaticFSApplication
from .ProxyFactory import ProxyFactory
from . import Logging as logging
from endpoint import Endpoint

PROJECT_DIR = path.find_in_ancestors('project.mk', __file__)
WISE_JS_DIR = path.resolve_path('wise', [PROJECT_DIR or "", '/usr/share/pyshared'])[0]


# Tornado has not support to dynamically adding new handlers for
# existing hosts. This will do it.
class TornadoApplication(web.Application):
    def append_handlers(self, host_pattern, host_handlers):
        if not host_pattern.endswith("$"):
            host_pattern += "$"

        specs = None
        for handler in self.handlers:
            if handler[0].pattern == host_pattern:
                specs = handler[1]
                break

        if not specs:
            self.add_handlers(host_pattern, host_handlers)
            return

        for spec in host_handlers:
            if isinstance(spec, tuple):
                assert len(spec) in (2, 3)
                pattern = spec[0]
                handler = spec[1]

                if len(spec) == 3:
                    kwargs = spec[2]
                else:
                    kwargs = {}
                spec = web.URLSpec(pattern, handler, kwargs)

            # replace old spec with new one
            assert isinstance(spec, web.URLSpec)
            for old in specs[:]:
                if old._path == spec._path:
                    specs.remove(old)
                    break

            specs.append(spec)


class Communicator(Thread):
    def __init__(self, host, port, properties={}):
        Thread.__init__(self)

        self.port = port
        self.host = host
        self.url = "http://{}:{}".format(self.host, self.port)
        assert isinstance(properties, dict)
        self._properties = properties
        self._adapters = {}

        self.is_ready = Event()
        self.daemon = True
        self.start()

    def getPropertiesForPrefix(self, prefix, remove_prefix=False):
        retval = {}
        for k, v in self._properties.items():
            if k.startswith(prefix):
                if remove_prefix:
                    k = k[len(prefix):]
                retval[k] = v

        return retval

    def getProperty(self, key):
        return self._properties.get(key, None)

    def getPropertyWithDefault(self, key, default):
        try:
            return self._properties[key]
        except KeyError:
            return default

    def run(self):
        prefix = "TornadoApp."
        properties = self.getPropertiesForPrefix(prefix, True)
        self._tornado = TornadoApplication(**properties)

        # NOTE: no_keep_alive is True, because otherwise, if the
        # handler is changed (or the communicator is destroyed and
        # created again), an old client will be served using the old
        # handler (binded on HTTPConnection)

        self._http_server = httpserver.HTTPServer(
            self._tornado, no_keep_alive=True)
        logging.info("Communicator: http server on {}:{}".format(self.host, self.port))
        self._http_server.listen(self.port, self.host)

        self._register_static_files_handler()
        self.is_ready.set()
        ioloop.IOLoop.instance().start()

    def shutdown(self):
        if not hasattr(self, "_http_server"):
            return

        self._http_server.stop()
        ioloop.IOLoop.instance().stop()

    def stringToProxy(self, stringfied_proxy):
        return ProxyFactory.create(self, stringfied_proxy)

    def proxyToString(self, proxy):
        return repr(proxy)

    def createObjectAdapter(self, name, endpoint):
        if name in self._adapters:
            raise AlreadyRegisteredException()

        if isinstance(endpoint, (str, unicode)):
            endpoint = Endpoint.from_string(endpoint)

        adapter = ObjectAdapter(self, name, endpoint)
        self._adapters[name] = adapter
        return adapter

    def registerApplication(self, application):
        self.registerHandlers(application.get_handler_spec())

    # handlers is a list of (url, class, params)
    def registerHandlers(self, handlers, host=".*$"):
        self._tornado.append_handlers(host, handlers)

    # return adapter name, find by its endpoint
    def resolveAdapter(self, endpoint):
        for name, adapter in self._adapters.items():
            if adapter.getEndpoint() == endpoint:
                return name

    # return adapter name, find by its endpoint
    def resolveEndpoint(self, adapter_name):
        adapter = self._adapters.get(adapter_name, None)
        if not adapter:
            return None
        return adapter.getEndpoint()

    def waitForShutdown(self):
        try:
            while True:
                self.join(1000)
                if not self.isAlive():
                    break
        except KeyboardInterrupt:
            pass

    def _register_static_files_handler(self):
        # register static files handler (to serve wise.js and others)
        static_files = StaticFSApplication(
            communicator=self, locator='/wise/', path=WISE_JS_DIR)
        self.registerApplication(static_files)

    def get_url(self, location):
        "returns a uri within the server"
        return "http://{}:{}/{}".format(self.host, self.port, location)

    def register_StaticFS(self, locator, path, index=''):
        frontend = StaticFSApplication(self, locator, path, index)
        self.registerApplication(frontend)
        return frontend
