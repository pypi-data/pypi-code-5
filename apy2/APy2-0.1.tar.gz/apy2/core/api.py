from .context import Context
from .function import Function
from .resource import Resource
from ..util.simple_match import smatch


class Api():

    def __init__(self):
        self._functions = {}
        self._resources = {}
        self._context = []

    def context(self, name=None):
        name = name or self.current_context()
        return Context(self, name)

    def current_context(self):
        if not self._context:
            return "root"
        return self._context[-1]

    def enter_context(self, name):
        self._context.append(name)

    def exit_context(self, name=None):
        if self._context:
            self._context.pop(-1)

    def add(self, name=None, context=None):
        from inspect import isfunction

        def decorator(x):
            if isfunction(x) or isinstance(x, Function):
                y = self._add_function(x, name, context)
            elif isinstance(x, Resource):
                y = self._add_resource(x, name, context)
            else:
                raise Exception("TODO: EXCEPTION")
            return y
        return decorator

    def _add_function(self, f, name, context):
        if hasattr(f, "_func"):
            f = f._func
        y = Function(f)
        y.name = name or y.name
        y.context = context or self.current_context()
        y.key = "%s.%s" % (str(y.context), str(y.name))
        self._functions[y.key] = y
        return y

    def _add_resource(self, r, name):
        raise NotImplementedError("add_resource")

    def find_functions(self, name="*", context=None):
        results = []
        context = context or self.current_context()
        for foo in self._functions.values():
            if smatch(foo.name, name) and smatch(foo.context, context):
                results.append(foo)
        return results

    def get_function(self, name, context=None):
        context = context or self.current_context()
        key = "%s.%s" % (str(context), str(name))
        if key in self._functions:
            return self._functions[key]
        return None
