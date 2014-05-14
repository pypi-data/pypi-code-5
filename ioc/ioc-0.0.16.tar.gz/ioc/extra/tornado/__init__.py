__author__ = 'rande'

class TornadoManager(object):
    STOPPED = 0
    STARTED = 1

    def __init__(self):
        self.ioloops = {}
        self.status = {}

    def add_ioloop(self, name, ioloop):
        self.ioloops[name] = ioloop
        self.status[name] = TornadoManager.STOPPED

    def stop(self, name):
        if self.status[name] == TornadoManager.STARTED:
            self.ioloops[name].stop()

    def start(self, name):
        if self.status[name] == TornadoManager.STOPPED:
            self.ioloops[name].start()

    def start_all(self):
        for name, loop in self.ioloops.iteritems():
            self.start(name)

    def stop_all(self):
        for name, loop in self.ioloops.iteritems():
            self.stop(name)
