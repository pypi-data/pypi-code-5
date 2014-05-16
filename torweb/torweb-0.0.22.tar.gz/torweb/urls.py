#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created: zhangpeng <zhangpeng@ivtime.com>

import re
from tornado.web import URLSpec
from code import interact

class Url(object):
    def __init__(self, prefix="/"):
        self.prefix = prefix
        self.handlers = []

    def __call__(self, url, **kwds):
        def _(cls):
            kwname = kwds.get("name", None)
            prefix = kwds.get("prefix") or self.prefix
            if not prefix.endswith("/"):
                prefix = prefix + "/"
            name = kwname or "%s.%s" % (cls.__module__, cls.__name__)
            #interact(local=locals())
            #url = re.sub("/{0,1}", self.prefix, url, 1)
            self.handlers.append(URLSpec(re.sub("/{0,1}", prefix, url, 1), cls, kwds, name=name))
            setattr(cls, "url_pattern", re.sub("/{0,1}", prefix, url, 1))
            return cls
        return _
url = Url()
except_url = Url()
