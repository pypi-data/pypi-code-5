

class Context():

    def __init__(self, api, name):
        self._api = api
        self._context = name
        for foo in self._api.find_functions(context=self._context):
            self.__dict__[foo.name] = foo

    def __enter__(self):
        self._api.enter_context(self._context)
        return self

    def __exit__(self, ty, val, trace):
        self._api.exit_context(self._context)

    def __repr__(self):
        c = self._context
        f = ""
        fs = [repr(f) for f in self._api.find_functions(context=self._context)]
        fs = ", ".join(fs)
        return "{context: '%s', functions: [%s]}" % (c, fs)

    def __eq__(self, o):
        if not isinstance(o, Context):
            return False
        return self._api == o._api and self._context == o._context
