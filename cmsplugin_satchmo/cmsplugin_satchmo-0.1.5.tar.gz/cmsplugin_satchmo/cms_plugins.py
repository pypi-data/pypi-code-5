# -*- coding: utf-8 -*-
from models import *

from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from product.models import Product, Category



class CMSSatchmoProductPlugin(CMSPluginBase):
	"""Main product plugin for Django CMS"""
	module = 'Satchmo Shop'
	model = SatchmoProductPlugin
	name = _('Product detail')
	render_template = 'cmsplugin_satchmo/product.html'
	raw_id_fields = ('product',)
	fields = ['product', 'title', 'product_url_path', 'style',]

	def render(self, context, instance, placeholder):
		if not hasattr(instance.product, 'site') or instance.product.site == Site.objects.get_current():
			site_url = ''
		else:
			site_url = '//%s' % instance.product.site.domain

		context.update({
			'site_url': site_url,
			'instance': instance,
			'placeholder': placeholder,
		})
		return context
plugin_pool.register_plugin(CMSSatchmoProductPlugin)


class CMSSatchmoProductsListingPlugin(CMSPluginBase):
	"""Main plugin for product listing in Django CMS"""
	module = 'Satchmo Shop'
	model = SatchmoProductsListPlugin
	name = _('Products listing')
	render_template = 'cmsplugin_satchmo/products_listing.html'
	fields = ['list_type', 'number', 'site', 'product_url_path', 'style',]

	def render(self, context, instance, placeholder):
		if not hasattr(instance, 'site') or instance.site == Site.objects.get_current():
			site_url = ''
		else:
			site_url = '//%s' % instance.site.domain

		products = Product.objects.active().filter(site=instance.site)

		if instance.list_type == RECENT_PRODUCTS_CHOICE_ID:
			products = products.order_by('-date_added', '-id')
		elif instance.list_type == BESTSELLERS_CHOICE_ID:
			products = products.order_by('-total_sold')
		elif instance.list_type == FEATURED_PRODUCTS_CHOICE_ID:
			products = products.filter(featured=True).order_by('?')
		else:
			raise ValueError('(cmsplugin_satchmo) List type is not defined in PRODUCTS_LISTING_CHOICES!')

		products = products[:instance.number]

		context.update({
			'products': products,
			'site_url': site_url,
			'instance': instance,
			'placeholder': placeholder,
		})
		return context
plugin_pool.register_plugin(CMSSatchmoProductsListingPlugin)



class CMSSatchmoCategoryPlugin(CMSPluginBase):
	"""Main category plugin for Django CMS"""
	module = 'Satchmo Shop'
	model = SatchmoCategoryPlugin
	name = _('Category detail')
	render_template = 'cmsplugin_satchmo/category.html'
	raw_id_fields = ('category',)
	fields = ['category', 'title', 'category_url_path', 'style',]

	def render(self, context, instance, placeholder):
		if not hasattr(instance.category, 'site') or instance.category.site == Site.objects.get_current():
			site_url = ''
		else:
			site_url = '//%s' % instance.category.site.domain

		category = Category.objects.get(id=instance.category_id)
		slug_list = [cat.slug for cat in category.parents()]
		if slug_list:
			slug_list = "/".join(slug_list) + "/"
		else:
			slug_list = ""

		context.update({
			'site_url': site_url,
			'parent_slugs': slug_list,
			'instance': instance,
			'placeholder': placeholder,
		})
		return context
plugin_pool.register_plugin(CMSSatchmoCategoryPlugin)



class CMSSatchmoCategoriesListPlugin(CMSPluginBase):
	"""Main plugin for categories listing in Django CMS"""
	module = 'Satchmo Shop'
	model = SatchmoCategoriesListPlugin
	name = _('Categories listing')
	render_template = 'cmsplugin_satchmo/categories_listing.html'
	fields = ['main_category', 'site', 'category_url_path', 'style',]

	def render(self, context, instance, placeholder):
		if not hasattr(instance, 'site') or instance.site == Site.objects.get_current():
			site_url = ''
		else:
			site_url = '//%s' % instance.site.domain

		categories = Category.objects.active().filter(site=instance.site)

		if instance.main_category:
			categories = categories.filter(parent=instance.main_category)
			slug_list = [cat.slug for cat in instance.main_category.parents()]
			slug_list = "/".join(slug_list) + "/"
		else:
			categories = categories.filter(parent=None)
			slug_list = ""

		context.update({
			'categories': categories.order_by('ordering'),
			'site_url': site_url,
			'parent_slugs': slug_list,
			'instance': instance,
			'placeholder': placeholder,
		})
		return context
plugin_pool.register_plugin(CMSSatchmoCategoriesListPlugin)


