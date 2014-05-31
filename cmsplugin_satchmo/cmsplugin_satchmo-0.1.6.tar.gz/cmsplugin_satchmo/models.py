# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin

from product.models import Product, Category

from settings import PRODUCT_URL_PATH, CATEGORY_URL_PATH

class MyCMSPlugin(CMSPlugin):
	style = models.CharField(_(u'class'), max_length=100, blank=True, help_text=_(u'Name of CSS class for template cusomization'))
	class Meta:
		abstract = True

class MyProductPlugin(MyCMSPlugin):
	product_url_path = models.CharField(_(u'satchmo product\'s URL path'), max_length=200, blank=True, default=PRODUCT_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and PRODUCT_SLUG as "products" fill "/shop/products/" here (ending slash "/" must be there). The path is used when you want links to products from another site.')
	)
	def save(self, *args, **kwargs):
		if self.product_url_path and self.product_url_path[-1:] != '/':
			self.product_url_path = self.product_url_path + '/'
		super(MyProductPlugin, self).save(*args, **kwargs)
	class Meta:
		abstract = True

class MyCategoryPlugin(MyCMSPlugin):
	category_url_path = models.CharField(_(u'satchmo category\'s URL path'), max_length=200, blank=True, default=CATEGORY_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and CATEGORY_SLUG as "category" fill "/shop/category/" here (ending slash "/" must be there). The path is used when you want links to categories from another site.')
	)
	def save(self, *args, **kwargs):
		if self.category_url_path and self.category_url_path[-1:] != '/':
			self.category_url_path = self.category_url_path + '/'
		super(MyCategoryPlugin, self).save(*args, **kwargs)
	class Meta:
		abstract = True

class SatchmoProductPlugin(MyProductPlugin):
	"""Model for the plugin for inlining a satchmo product"""
	product = models.ForeignKey(Product, verbose_name=_(u'product'), limit_choices_to={'active': True})
	title = models.CharField(_(u'title'), max_length=200, blank=True)


RECENT_PRODUCTS_CHOICE_ID = 1
BESTSELLERS_CHOICE_ID = 2
FEATURED_PRODUCTS_CHOICE_ID = 3

PRODUCTS_LISTING_CHOICES = (
	(RECENT_PRODUCTS_CHOICE_ID, _(u'recent products'),),
	(BESTSELLERS_CHOICE_ID, _(u'bestsellers'),),
	(FEATURED_PRODUCTS_CHOICE_ID, _(u'featured products'),),
)

class SatchmoProductsListPlugin(MyProductPlugin):
	"""Model for the plugin of product listing"""
	list_type = models.PositiveSmallIntegerField(_(u'kind of list'), choices=PRODUCTS_LISTING_CHOICES)
	number = models.PositiveSmallIntegerField(_(u'number'), default=5)
	site = models.ForeignKey(Site, verbose_name=_(u'products list from site'))



class SatchmoCategoryPlugin(MyCategoryPlugin):
	"""Model for the plugin of category detail"""
	category = models.ForeignKey(Category, verbose_name=_(u'category'), limit_choices_to={'is_active': True})
	title = models.CharField(_(u'title'), max_length=200, blank=True)



class SatchmoCategoriesListPlugin(MyCategoryPlugin):
	main_category = models.ForeignKey(Category, verbose_name=_(u'main category'), limit_choices_to={'is_active': True}, blank=True, null=True,
		help_text=_(u'Leave blank for listing root categories or select main category for listing their child categries.')
	)
	site = models.ForeignKey(Site, verbose_name=_(u'categories list from site'))
