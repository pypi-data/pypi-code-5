import requests

class RateFetchError(requests.exceptions.RequestException):
	""" Encapsulates all possible requests errors """
	pass