# -*- coding: utf-8 -*-
"""Settings for cmsplugin_satchmo"""

from django.conf import settings

CMSPLUGIN_SATCHMO_SETTINGS = getattr(settings, 'SATCHMO_SETTINGS', {
	'SHOP_BASE': '/',
	'PRODUCT_SLUG': 'products',
	'CATEGORY_SLUG': 'category',
})
PRODUCT_URL_PATH = '%s%s/' % (CMSPLUGIN_SATCHMO_SETTINGS['SHOP_BASE'], CMSPLUGIN_SATCHMO_SETTINGS['PRODUCT_SLUG'])
CATEGORY_URL_PATH = '%s%s/' % (CMSPLUGIN_SATCHMO_SETTINGS['SHOP_BASE'], CMSPLUGIN_SATCHMO_SETTINGS['CATEGORY_SLUG'])

