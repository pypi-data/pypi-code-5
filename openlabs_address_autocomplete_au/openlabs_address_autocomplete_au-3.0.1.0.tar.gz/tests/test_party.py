# -*- coding: utf-8 -*-
"""
    Tests Party

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import warnings
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TestParty(unittest.TestCase):
    '''
    Test Party
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('address_autocomplete_au')

        self.Party = POOL.get('party.party')
        self.Country = POOL.get('country.country')
        self.Address = POOL.get('party.address')
        self.Subdivion = POOL.get('country.subdivision')
        self.PartyConfiguration = POOL.get('party.configuration')

    def create_defaults(self):
        """
        Create default records
        """
        self.australia, self.india = self.Country.create([{
            'name': 'Australia',
            'code': 'AU',
        }, {
            'name': 'India',
            'code': 'IN',
        }])

        self.subdivision, = self.Subdivion.create([{
            'country': self.australia.id,
            'name': 'New South Wales',
            'code': 'AU-NSW',
            'type': 'state'
        }])

    def test0010_check_address_autocompletion(self):
        """
        Check auto completion of address
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.create_defaults()

            values = dict.fromkeys(['zip', 'city', 'subdivision', 'party'])

            self.PartyConfiguration.create([{
                'auspost_api_key': '12c5385b-21a8-4a16-8709-10a87ac5ed27'
            }])

            party, = self.Party.create([{
                'name': 'Test Party',
                'addresses': [
                    ('create', [{
                        'name': 'Test Address',
                    }])
                ]
            }])

            values['party'] = party.id

            # Check subdivision and city with zip code as None
            address = self.Address(**values)
            result = address.autocomplete_zip()
            self.assertFalse(result)

            result = address.on_change_zip()
            self.assertFalse(result)

            # Check subdivision and city with zip code
            values['zip'] = '2046'
            address = self.Address(**values)
            result = address.autocomplete_zip()
            self.assertTrue('RODD POINT, 2046, NSW' in result)

            values['zip'] = '204'
            address = self.Address(**values)
            result = address.autocomplete_zip()
            self.assertTrue('RODD POINT, 2046, NSW' in result)

            # Check with autofilled value
            values['zip'] = 'RODD POINT, 2046, NSW'
            address = self.Address(**values)
            result = address.autocomplete_zip()
            self.assertFalse(result)

            result = address.on_change_zip()
            self.assertEqual(result['subdivision'], self.subdivision.id)
            self.assertEqual(result['zip'], '2046')
            self.assertEqual(result['city'], 'RODD POINT')

            # Check with invalid value
            values['zip'] = 'RODD POINT, 1134'
            address = self.Address(**values)
            result = address.on_change_zip()
            self.assertFalse(result)

            # Check autocomplete when city, zip and subdivision are
            # already filled
            values['zip'] = '2046'
            values['city'] = 'RODD POINT'
            values['subdivision'] = self.subdivision.id
            address = self.Address(**values)
            result = address.autocomplete_zip()
            self.assertFalse(result)

    def test0015_check_address_autocompletion_without_api_key(self):
        """
        Check auto completion of address without api key
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.create_defaults()

            party, = self.Party.create([{
                'name': 'Test Party',
                'addresses': [
                    ('create', [{
                        'name': 'Test Address',
                    }])
                ]
            }])

            values = dict.fromkeys(['zip', 'city', 'subdivision', 'party'])
            values['party'] = party.id

            values['zip'] = '12333'
            address = self.Address(**values)

            # Should raise warning since API key is not configured, though
            # it wont effect saving of record
            with warnings.catch_warnings(record=True) as w:
                address.autocomplete_zip()
                self.assertEqual(len(w), 1)
                self.assertEqual(
                    w[0].message[0],
                    "API Key not found! \n"
                    "Please configure API key in Party Configuration to enable"
                    " autocompletion of address.",
                )
            address.save()

    def test0018_check_address_autocompletion_no_matching_records(self):
        """
        Check auto completion of address when no matching records found
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.create_defaults()

            self.PartyConfiguration.create([{
                'auspost_api_key': '12c5385b-21a8-4a16-8709-10a87ac5ed27'
            }])

            party, = self.Party.create([{
                'name': 'Test Party',
                'addresses': [
                    ('create', [{
                        'name': 'Test Address',
                    }])
                ]
            }])

            values = dict.fromkeys(['zip', 'city', 'subdivision', 'party'])
            values['party'] = party.id

            values['zip'] = '12333'
            address = self.Address(**values)

            # Should raise warning since there is no such zip in
            # australia
            with warnings.catch_warnings(record=True) as w:
                result = address.autocomplete_zip()
                self.assertFalse(result)
                self.assertEqual(len(w), 1)
                self.assertEqual(w[0].message[0], 'No matching address found!')
            address.save()

    def test0018_check_address_autocompletion_with_zip_less_than3(self):
        """
        Check auto completion of address when zip code is less than 3 chars
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.create_defaults()

            self.PartyConfiguration.create([{
                'auspost_api_key': '12c5385b-21a8-4a16-8709-10a87ac5ed27'
            }])

            party, = self.Party.create([{
                'name': 'Test Party',
                'addresses': [
                    ('create', [{
                        'name': 'Test Address',
                    }])
                ]
            }])

            values = dict.fromkeys(['zip', 'city', 'subdivision', 'party'])
            values['party'] = party.id

            values['zip'] = '12'
            address = self.Address(**values)

            # Should raise warning
            with warnings.catch_warnings(record=True) as w:
                result = address.autocomplete_zip()
                self.assertFalse(result)
                self.assertEqual(len(w), 1)
                self.assertEqual(
                    w[0].message[0],
                    'Please enter at least 3 characters for Suburb, Town, '
                    'City or Postcode.'
                )
            address.save()

    def test0020_validate_country(self):
        """
        Check if country is valid
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.create_defaults()

            party, = self.Party.create([{
                'name': 'Test Party',
                'addresses': []
            }])

            address, = self.Address.create([{
                'name': 'Test Address',
                'party': party.id
            }])

            self.assertEqual(address.country.name, self.australia.name)

            # Try setting country other than australia and it will raise
            # error
            with self.assertRaises(UserError):
                address, = self.Address.create([{
                    'name': 'Test Address',
                    'party': party.id,
                    'country': self.india.id
                }])


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestParty)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
