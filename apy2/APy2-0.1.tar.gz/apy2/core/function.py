

class Function():

    def __init__(self, func):
        from inspect import getdoc
        self._func = func
        self.name = func.__name__
        self.context = "root"
        self.key = "%s.%s" % (self.context, self.name)
        self._get_signature(func)
        self.doc = getdoc(func)

    def _get_signature(self, foo):
        from inspect import signature, getfullargspec
        self.sign = signature(foo)
        self.argspec = getfullargspec(foo)

    def get_args(self):
        return self.argspec[0][:]

    def call(self, *args, **kwargs):
        if not self._check_args(*args, **kwargs):
            raise Exception("TODO: EXCEPTION")
        return self._func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def _check_args(self, *args, **kwargs):
        ok = True
        for n, (name, par) in enumerate(self.sign.parameters.items()):
            if n < len(args):
                ok = ok and (type(args[n]) == par.annotation
                             or par.annotation == par.empty)
            else:
                if name in kwargs:
                    ok = ok and (type(kwargs[name]) == par.annotation
                                 or par.annotation == par.empty)
                else:
                    ok = ok and par.default != par.empty
        return ok

    def to_json(self):
        return {"context": self.context, "name": self.name, "args": self.get_args()}

    def __repr__(self):
        from inspect import formatargspec
        argspec = formatargspec(*self.argspec)
        return "<%s%s>" % (self.key, argspec)
