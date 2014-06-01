# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Update handling.

Versions are identified by integers.

The current code version is given by the `VERSION` definition
in this module. The current database version is specified
by `config[-2].value` in the database (or is 1, if this does not exist).
This module contains functions `update*i*` to update the database
version from *i* to *i+1*.
"""

VERSION = 2

from config import Config

_md = globals()

def update():
  c = Config()
  try: dbv = int(c.get(-2, KeyError).value)
  except KeyError: dbv = 1
  while dbv < VERSION:
    _md["update%d" % dbv]()
    c.update_item(id=-2, value=dbv)
    dbv += 1


def update1():
  c = Config().cursor()
  # create the config database
  c.execute("create table reseller.config(name text not null, value text) inherits(item)")
  # add `version` config information
  c.execute("insert into reseller.config(id, name, value, active) values (-2, 'version', '1', FALSE)")
##  # adapt the data model for stock support
##  c.execute("alter table reseller.client_delivery_item add article_id int not null")
##  c.execute("update reseller.client_delivery_item set article_id = (select article_id from reseller.provider_delivery_item where id = provider_delivery_item_id)")
##  c.execute("alter table reseller.client_delivery_item drop provider_delivery_item_id")
##  c.execute("alter table reseller.client_delivery alter provider_delivery_id drop not null")

