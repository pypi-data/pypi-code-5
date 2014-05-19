# -*- coding: utf-8 -*-
"""
    Party

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from auspost import API
import warnings

from trytond.pool import Pool, PoolMeta

__metaclass__ = PoolMeta
__all__ = ['Address']


class Address:
    "Address"
    __name__ = "party.address"

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()

        # Allow country to be filled with Australia only
        cls.country.domain = [('code', '=', 'AU')]

        autocomplete_list = ['city', 'zip', 'subdivision']

        # Fill city and subdivision on the basis of zip code
        cls.zip.autocomplete = autocomplete_list
        cls.zip.depends = autocomplete_list

        # Right after the value is filled in zip, if it has information
        # separated by commas, its probably info that needs to be filled
        # into city, subdivision and zip.
        cls.zip.on_change = ['zip']

    def autocomplete_zip(self):
        """
        Returns list of strings on the basis of zip where each string is a
        combination of australia city, postcode and state
        """
        # If zip, city and subdivision are already there, do not proceed
        if self.zip and self.city and self.subdivision:
            return []

        if self.zip and ',' not in self.zip:
            return self._get_auspost_details()
        return []

    def on_change_zip(self):
        """
        Updates values for subdivision and city if zip is changed
        """
        Subdivision = Pool().get('country.subdivision')

        if self.zip and ',' in self.zip:
            try:
                city, zip, state = self.zip.split(', ')
            except ValueError:
                return {}
            else:
                subdivision, = Subdivision.search([
                    ('code', '=', 'AU-%s' % (state, ))
                ])
                return {
                    'city': city,
                    'zip': zip,
                    'subdivision': subdivision.id,
                }
        return {}

    @staticmethod
    def default_country():
        """
        Set Australia as default country
        """
        Country = Pool().get('country.country')

        country, = Country.search([('code', '=', 'AU')])
        return country.id

    def _get_auspost_details(self):
        """
        Calls australia webservice api to search matched address details
        on the basis of zip code

        Returns corresponding subdivision and postcode of Australia for given
        zip code

        :param search_key: Zip code to search postcode with
        """
        Configuration = Pool().get('party.configuration')

        api_key = Configuration(1).auspost_api_key

        if not api_key:
            warnings.warn(
                "API Key not found! \n"
                "Please configure API key in Party Configuration to enable "
                "autocompletion of address.", UserWarning
            )
            return []

        api = API(api_key)
        result = api.postcode_search(self.zip)

        if result.get('error'):
            warnings.warn(
                "%s" % result['error']['errorMessage'], UserWarning
            )
            return []

        if not result['localities']:
            warnings.warn(
                "No matching address found!", UserWarning
            )
            return []

        # It assumes api will return list of records since one zip
        # code is used for multiple locations
        locations = result['localities']['locality']

        return [
            ', '.join([loc['location'], str(loc['postcode']), loc['state']])
            for loc in locations
        ]
