# -*- coding: utf-8 -*-

import colander
from .fields import MsgFields as F


class _MetaSchema(colander.Schema):
    start_time = colander.SchemaNode(colander.String(), name=F.META_START_TIME)
    end_time = colander.SchemaNode(colander.String(), name=F.META_END_TIME)
    err = colander.SchemaNode(colander.String(), name=F.META_ERR, missing=None)
    msg = colander.SchemaNode(colander.String(), name=F.META_MSG, missing=None)


class _BaseTaskSchema(colander.Schema):
    meta = _MetaSchema(name=F.META)


class TestSchema(_BaseTaskSchema):
    # A stable schema for testing purposes.
    a = colander.SchemaNode(colander.String(), name="a")
    b = colander.SchemaNode(colander.String(), name="b", missing=None)
    uni = colander.SchemaNode(colander.String(), name="テスト", missing=None)


# ###### Actual Task schema definitions ########

class WhoisSchema(_BaseTaskSchema):
    whois_raw = colander.SchemaNode(colander.String(), name=F.WHOIS_RAW)
