import requests
from decimal import Decimal
from django.conf import settings

from exchange.exceptions import RateFetchError

if settings.OPENEXCHANGERATES_PAID_CX:
	BASE_URL = 'https://openexchangerates.org/api/'
else:
	BASE_URL = 'http://openexchangerates.org/api/'

LATEST_URL = BASE_URL + 'latest.json'
CURRENCY_URL = BASE_URL + 'currencies.json'

class RateFetchClient(object):
	"""
	This class creates an object for fetching
	and dealing with exchange rates.

	"""

	def __init__(self, key=None):
		"""
		Creates a new fetcher instance

		"""
		self.fetcher = requests.Session()
		if not key:
			key = settings.OPENEXCHANGERATES_APP_ID
		self.fetcher.params.update({'app_id': key})

	def query_rates(self, base=None):
		"""
		Fetches the rates JSON object from 
		the `OPENEXCHANGERATES_LATEST_URL` API gateway

		Refer to http://openexchangerates.org for more 
		information

		"""
		try:

			r = self.fetcher.get(LATEST_URL)
			
			if base and settings.OPENEXCHANGERATES_PAID_CX:
				r = self.fetcher.get(LATEST_URL, params={'base': base.upper()})
			r.raise_for_status()
			
			return r.json(parse_int=Decimal, parse_float=Decimal)['rates']

		except requests.exceptions.RequestException, error:
			raise RateFetchError(error)

	def restrict_rates(self, base=None, symbols=None):
		"""
		Makes a more restrictive query for 
		particular currencies.

		:param symbols:
			This is a list of currency codes for which 
			we would like exchange rates returned

		:param base:
			The base currency we would like for our 
			returned JSON. Take a look at 'http://openexchangerates.org'

		:return:
			Currency dictionary

		Note that only users signed up for the Ultimate or Enterprise
		plans may make use of this particular method

		"""
		param = {}
		if base:
			param['base'] = base.upper()

		if symbols:
			symbols = ','.join(symbols)
			param['symbols'] = symbols.upper()

		try:
			r = self.fetcher.get(LATEST_URL, params=param)
		except requests.exceptions.RequestException, error:
			raise RateFetchError(error)

		return r.json(parse_int=Decimal, parse_float=Decimal)['rates']

	def query_currency(self):
		"""
		Fetch a list of currencies

		"""
		try:
			r = self.fetcher.get(CURRENCY_URL)
			return r.json()
		except requests.exceptions.RequestException, error:
			raise RateFetchError(error)

	def exchange_currency(self, amount, _from, _to, rate=False):
		"""
		Using the base currency provided, this works on the 
		premise that if, for instance, 
		==> 1USD == 1.08CAD and 1USD == 0.73EUR, 
		==> then 1USD == 1.08CAD == 0.73EUR, 

		which means that 
		
		==> 1CAD == ((0.73 * 1) / 1.08) EUR. 

		Following this logic ...

		:param amount:
			The amount to be converted

		:param _from:
			The currency from which the exchange is to be made

		:param _to:
			The currency to which the exchange is to be made

		:param rate:
			If True, returns the conversion rate alongside 
			the converted amount

		:return:
			The converted amount intended in the "_to" currency
			(See above regarding the return of conversion rates)

		"""
		_from = _from.upper()
		_to = _to.upper()

		try:
			rates = self.query_rates()
		except requests.exceptions.RequestException, error:
			raise RateFetchError(error)

		if _from in rates and _to in rates:

			conv_rate = rates[_to] / rates[_from]
			amount = amount * conv_rate
			if rate:
				return (amount, conv_rate)
			else: return amount

		raise Exception('Unable to convert funds. Please try again.')
