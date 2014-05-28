# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin

from product.models import Product, Category

from settings import PRODUCT_URL_PATH, CATEGORY_URL_PATH

class SatchmoProductPlugin(CMSPlugin):
	"""Model for the plugin for inlining a satchmo product"""
	product = models.ForeignKey(Product, verbose_name=_(u'product'), limit_choices_to={'active': True})
	title = models.CharField(_(u'title'), max_length=200, blank=True)
	product_url_path = models.CharField(_(u'satchmo product\'s URL path'), max_length=200, blank=True, default=PRODUCT_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and PRODUCT_SLUG as "products" fill "/shop/products" here. The path is used when you want link to a product from another site.')
	)
	style = models.CharField(_(u'class'), max_length=100, blank=True, help_text=_(u'Name of CSS class for template cusomization'))


RECENT_PRODUCTS_CHOICE_ID = 1
BESTSELLERS_CHOICE_ID = 2
FEATURED_PRODUCTS_CHOICE_ID = 3

PRODUCTS_LISTING_CHOICES = (
	(RECENT_PRODUCTS_CHOICE_ID, _(u'recent products'),),
	(BESTSELLERS_CHOICE_ID, _(u'bestsellers'),),
	(FEATURED_PRODUCTS_CHOICE_ID, _(u'featured products'),),
)

class SatchmoProductsListPlugin(CMSPlugin):
	"""Model for the plugin of product listing"""
	list_type = models.PositiveSmallIntegerField(_(u'kind of list'), choices=PRODUCTS_LISTING_CHOICES)
	number = models.PositiveSmallIntegerField(_(u'number'), default=5)
	site = models.ForeignKey(Site, verbose_name=_(u'products list from site'))
	product_url_path = models.CharField(_(u'satchmo product\'s URL path'), max_length=200, blank=True, default=PRODUCT_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and PRODUCT_SLUG as "products" fill "/shop/products" here. The path is used when you want links to products from another site.')
	)
	style = models.CharField(_(u'class'), max_length=100, blank=True, help_text=_(u'Name of CSS class for template cusomization'))



class SatchmoCategoryPlugin(CMSPlugin):
	"""Model for the plugin of category detail"""
	category = models.ForeignKey(Category, verbose_name=_(u'category'), limit_choices_to={'is_active': True})
	title = models.CharField(_(u'title'), max_length=200, blank=True)
	category_url_path = models.CharField(_(u'satchmo category\'s URL path'), max_length=200, blank=True, default=CATEGORY_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and CATEGORY_SLUG as "category" fill "/shop/category" here. The path is used when you want link to a category from another site.')
	)
	style = models.CharField(_(u'class'), max_length=100, blank=True, help_text=_(u'Name of CSS class for template cusomization'))



class SatchmoCategoriesListPlugin(CMSPlugin):
	site = models.ForeignKey(Site, verbose_name=_(u'categories list from site'))
	category_url_path = models.CharField(_(u'satchmo category\'s URL path'), max_length=200, blank=True, default=CATEGORY_URL_PATH,
		help_text=_(u'E.g. if in your SATCHMO_SETTINGS are defined SHOP_BASE as "/shop/" and CATEGORY_SLUG as "category" fill "/shop/category" here. The path is used when you want links to categories from another site.')
	)
	style = models.CharField(_(u'class'), max_length=100, blank=True, help_text=_(u'Name of CSS class for template cusomization'))
