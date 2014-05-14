#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created: zhangpeng <zhangpeng@ivtime.com>

from tornado.web import URLSpec
from code import interact

class Url(object):
    def __init__(self):
        self.handlers = []

    def __call__(self, url, **kwds):
        def _(cls):
            kwname = kwds.get("name", None)
            name = kwname or "%s.%s" % (cls.__module__, cls.__name__)
            self.handlers.append(URLSpec(url, cls, kwds, name=name))
            return cls
        return _
url = Url()
except_url = Url()
