import drest

from .endpoints import CUCKOO_EP


class CuckooAPI(drest.API):
    """Interface with cuckoo's REST API."""
    def __init__(self, *args, **kwargs):
        super(CuckooAPI, self).__init__(*args, **kwargs)
        for methods, name, path, desc in CUCKOO_EP:
            self.add_resource(name, path=path)
            docstring = '[{methods}] {desc}'.format(
                methods='|'.join(methods),
                desc=desc)
            getattr(self, name).__doc__ = docstring

    class Meta:
        trailing_slash = False
