import ujson


class EventObligatoryKeysException(Exception):
    pass


class Event(object):
    """
    Event represents data to be sent to the Message Oriented Middleware.
    """

    obligatory_keys = []

    def __init__(self, **kw):
        if set(self.obligatory_keys) - set(kw.keys()):
            raise EventObligatoryKeysException
        self.arguments = kw

    def to_json(self):
        return ujson.dumps(self.arguments)

    def __str__(self):
        return "%s %r" % (self.__class__.__name__, self.arguments)


class SemanticEvent(Event):
    obligatory_keys = ["instance", "klass", "graph", "action"]
