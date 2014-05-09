
from collections import namedtuple, Iterable

Request = namedtuple('Request', ['url', 'method', 'params', 'headers'])

Advanced = namedtuple('Advanced', ['f', 'o', 'v'])

class BugBuilder:

    def __init__(self, endpoint="https://bugzilla.mozilla.org", credentials=None, token=None):
        if credentials and token:
            raise Exception("Cannot specify both credentials and token")
        self._endpoint = endpoint
        self._credentials = credentials
        self._token = token
        self._id = None
        self._ids = None
        self._fields = []
        self._product = None
        self._component = None
        self._status = None
        self._advanced = []

    def id(self, id):
        if self._ids:
            raise Exception("Can't specify both id and ids")
        if not isinstance(id, int):
            raise Exception("id() takes an int")
        self._id = id
        return self

    def ids(self, ids):
        if self._id:
            raise Exception("Can't specify both id and ids")
        if not isinstance(ids, Iterable):
            raise Exception("ids() takes an iterable of ints")
        ids = list(ids)
        if not all(isinstance(id, int) for id in ids):
            raise Exception("ids() takes an iterable of ints")
        self._ids = ids
        return self

    def fields(self, *fields):
        if not all(isinstance(field, basestring) for field in fields):
            raise Exception("fields() takes a variable number of strings")
        self._fields = fields
        return self

    def product(self, *product):
        if not all(isinstance(p, basestring) for p in product):
            raise Exception("product() takes a variable number of strings")
        self._product = product
        return self

    def component(self, *component):
        if not all(isinstance(c, basestring) for c in component):
            raise Exception("component() takes a variable number of strings")
        self._component = component
        return self

    def status(self, *status):
        if not all(isinstance(s, str) for s in status):
            raise Exception("status() takes a variable number of strings")
        for s in status:
            if s not in ("UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "READY", "RESOLVED", "VERIFIED"):
                raise Exception("status() does not take '%s' as a valid status" % s)
        self._status = status
        return self

    def open(self):
        self._status = ("UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED")
        return self

    def closed(self):
        self._status = ("READY", "RESOLVED", "VERIFIED")
        return self

    def advanced(self, field, operation, value):
        self._advanced.append(Advanced(field, operation, value))
        return self

    def build(self):
        params = {}
        if self._token:
            params["token"] = self._token
        if self._credentials:
            params["login"] = self._credentials[0]
            params["password"] = self._credentials[1]
        headers = {"Content-Type": "application/json"}
        if self._id:
            url = "%s/rest/bug/%d" % (self._endpoint, self._id)
        else:
            url = "%s/rest/bug" % self._endpoint
        if self._ids:
            params["id"] = ','.join(str(id) for id in self._ids)
        if self._fields:
            params["include_fields"] = ','.join(str(f) for f in self._fields)
        if self._product:
            params["product"] = self._product
        if self._component:
            params["component"] = self._component
        if self._status:
            params["status"] = self._status
        for i,a in enumerate(self._advanced, start=1):
            params["f%d" % i] = a.f
            params["o%d" % i] = a.o
            params["v%d" % i] = a.v
        return Request(url, "GET", params, headers)
