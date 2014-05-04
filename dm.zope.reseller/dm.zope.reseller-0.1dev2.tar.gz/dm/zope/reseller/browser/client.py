# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from plone.z3cform.crud.crud import NullForm

from ..client import Clients as ClientsCollection

from .view import CrudMixin, UdMixin, SearchMixin, make_readonly_fields
from .traversal import CollectionProxy, Constant


class Clients(CollectionProxy):
  obj = Constant(ClientsCollection())


class ClientsCrud(CrudMixin):
  css_class = "client"


class ClientsSearch(SearchMixin):
  css_class = "client"


class Client(CollectionProxy): pass


class ClientCrud(UdMixin):
  url_pattern = "++child++%s"


class Delivery(CollectionProxy): pass

class DeliveryCrud(UdMixin):
  url_pattern = None
  def item_edit_check(*unused): return False
  item_delete_check = item_edit_check

  @property
  def crud_fields(self):
    return make_readonly_fields(super(DeliveryCrud, self).crud_fields.omit("state"))
