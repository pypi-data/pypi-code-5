from decimal import Decimal
from django.conf import settings
from django.test import TestCase

from exchange.exceptions import RateFetchError
from exchange import RateFetchClient

class RateFetchTests(TestCase):
	# Tests the RateFetchClient

	def setUp(self):
		self.fetcher = RateFetchClient(settings.OPENEXCHANGERATES_APP_ID)

	def tearDown(self):
		self.fetcher.fetcher.close()

	def test_initialization(self):
		# Test that the app_id parameter is added 
		# to the newly initialized :class:RateFetchClient
		self.assertTrue('app_id' in self.fetcher.fetcher.params)

	def test_query_rates(self):
		# Assert that we do indeed have a
		# JSON response from the API endpoint
		response = self.fetcher.query_rates()
		self.assertIsInstance(response, dict)
		self.assertTrue('USD' in response)

	def test_query_currency(self):
		# Assert that a dictionary
		# of currencies is returned
		response = self.fetcher.query_currency()
		self.assertIsInstance(response, dict)
		self.assertTrue('USD' in response)

	def test_exchange_currency(self):
		# Test that currencies are exchanged
		amnt = Decimal('15.00')
		amount = self.fetcher.exchange_currency(amnt, 'UsD', 'cAd', True)
		self.assertIsInstance(amount, tuple)

		amount = self.fetcher.exchange_currency(amnt, 'uSd', 'cad')
		self.assertIsInstance(amount, Decimal)

		self.assertRaises(Exception, lambda: self.fetcher.exchange_currency(amnt, 'bore', 'cad'))
