# vim: fileencoding=utf8:et:sw=4:ts=8:sts=4

import signal

import yaml

ADDED = 1
MODIFIED = 2
REMOVED = 3


class Config(object):
    def __init__(self, filepath, sig=signal.SIGUSR1):
        self._filepath = filepath
        self._signal = sig
        self._loaded = False
        self._data = {}
        self._watchers = {}

    def load(self):
        with open(self._filepath, 'r') as fp:
            raw = fp.read()
        newconfig = yaml.load(raw, Loader=yaml.CSafeLoader)
        oldconfig = self._data.copy()

        for name, value in newconfig.iteritems():
            self._set(name, value)

        for name, value in oldconfig.iteritems():
            if name not in newconfig:
                del self._data[name]
                for watcher in self._watchers.get(name, []):
                    watcher(name, value, None, REMOVED)

        if not self._loaded and self._signal is not None:
            signal.signal(self._signal, self._sighandler)

        self._loaded = True

    def get(self, name, default=None):
        return self._data.get(name, default)

    __getitem__ = get

    def watch(self, name, handler=None):
        if handler is None:
            # support @conf.watch(name) decorator usage
            return lambda h: watch(name, h)
        self._watchers.setdefault(name, []).append(handler)

    def _sighandler(self, signum, frame):
        self.load()

    def _set(self, name, value):
        was_present = False
        old = None
        if name in self._data:
            was_present = True
            old = self._data[name]

        self._data[name] = value

        if not was_present:
            for watcher in self._watchers.get(name, []):
                watcher(name, None, value, ADDED)
        elif old != value:
            for watcher in self._watchers.get(name, []):
                watcher(name, old, value, MODIFIED)
