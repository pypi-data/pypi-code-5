from .base.obj import BaseObject
from .base.fields import ObjectProperty
from .base.fields import ObjectCollectionProperty

from .product import Product
from .product import Vendor
from .product import Category


class Site(BaseObject):

  name = ObjectProperty()
  title = ObjectProperty()

  preferred_url = ObjectProperty()
  permanent_url = ObjectProperty()

  products = ObjectCollectionProperty(
      cls=Product,
      loader=lambda id_, d: d.products)
  vendors = ObjectCollectionProperty(
      cls=Vendor,
      loader=lambda id_, d: d.vendors)
  categories = ObjectCollectionProperty(
      cls=Category,
      loader=lambda id_, d: d.categories)

  currency = ObjectProperty()
  unit_system = ObjectProperty()
