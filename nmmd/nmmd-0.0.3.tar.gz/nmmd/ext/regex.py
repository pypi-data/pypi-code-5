import re

from nmmd import Dispatcher


class RegexDispatcher(Dispatcher):

    def prepare(self):
        data = []
        for invoc, method in self.registry:
            args, kwargs = self.loads(invoc)
            rgx = re.compile(*args, **kwargs)
            data.append((rgx, method))
        return data

    def gen_methods(self, string):
        for rgx, methodname in self.dispatch_data:
            matchobj = rgx.match(string)
            if matchobj:
                method = getattr(self.inst, methodname)
                yield method, (string, matchobj)

        # Else try inst.generic_handler
        generic = getattr(self.inst, 'generic_handler', None)
        if generic is not None:
            yield generic

    def apply_handler(self, method_data, *args, **kwargs):
        '''Call the dispatched function, optionally with other data
        stored/created during .register and .prepare. Assume the arguments
        passed in by the dispathcer are the only ones required.
        '''
        if isinstance(method_data, tuple):
            len_method = len(method_data)
            method = method_data[0]
            if 1 < len_method:
                args = method_data[1]
            if 2 < len_method:
                kwargs = method_data[2]
        else:
            method = method_data
        return method(*args, **kwargs)
