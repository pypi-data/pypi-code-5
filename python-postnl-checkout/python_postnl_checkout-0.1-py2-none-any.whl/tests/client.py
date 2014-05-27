import datetime
import decimal
import unittest

from httmock import HTTMock

from ..client import PostNLCheckoutClient

from .base import PostNLTestMixin


class ClientTests(PostNLTestMixin, unittest.TestCase):
    # IntRef used for testing
    intref = 'a0713e4083a049a996c302f48bb3f535'

    def setUp(self):
        """ Instantiate client for tests. """

        def response(url, request):
            if '.xsd' in url.path:
                # Request of XSD file from WSDL
                filename = url.path.rsplit('/', 1)[1]

                return self.read_file('wsdl/' + filename)

            # Request for WSDL file
            self.assertEquals(
                url.geturl(),
                PostNLCheckoutClient.SANDBOX_ENDPOINT_URL
            )

            return self.read_file('wsdl/WebshopCheckoutWebService_1.wsdl')

        with HTTMock(response):
            self.client = PostNLCheckoutClient(
                username='klant1',
                # Note: sha1 hashed password:
                # dd7b7b74ea160e049dd128478e074ce47254bde8
                password='xx',
                webshop_id='a0713e4083a049a996c302f48bb3f535',
                environment='sandbox'
            )

    def assertWebshop(self, result):
        """ Assert webshop and id in result. """

        self.assertIn('Webshop', result)
        self.assertIn('IntRef', result['Webshop'])
        self.assertEquals(result['Webshop']['IntRef'], self.intref)

    def test_client(self):
        """ Test instantiated client """

        # Get suds client
        self.assertTrue(hasattr(self.client, 'suds_client'))

        # Make sure we have a service
        self.assertTrue(hasattr(self.client, 'service'))
        service = self.client.service

        # Make sure necessary methods are available
        self.assertTrue(hasattr(service, 'ReadOrder'))
        self.assertTrue(hasattr(service, 'ConfirmOrder'))
        self.assertTrue(hasattr(service, 'UpdateOrder'))
        self.assertTrue(hasattr(service, 'PingStatus'))

    def test_add_webshop(self):
        """ Test _add_webshop """

        kwargs = {
            'kaas': 'lekker'
        }

        self.client._add_webshop(kwargs)

        # Kwargs should be updated with IntRef
        self.assertEquals({
            'kaas': 'lekker',
            'Webshop': {'IntRef': self.intref}
        }, kwargs)

    def test_sudsobject_to_dict(self):
        """ Test _sudsobject_to_dict(obj, wrapper). """

        # Trivial test; input should be output
        data = {
            'Order': {
                'ExtRef': '1105_900',
            },
            'ListTest': [1, 2, 3]
        }

        output = self.client._sudsobject_to_dict(data)

        self.assertEquals(output, data)

    def test_parse_datetime(self):
        """ Test parsing datetimes """
        output = self.client._parse_datetime('15-06-1977 00:00:00')

        self.assertEquals(
            output,
            datetime.datetime(
                year=1977, month=6, day=15,
                hour=0, minute=0, second=0
            )
        )

    def test_format_datetime(self):
        """ Test parsing datetimes """
        test_date = datetime.datetime(
            year=1977, month=6, day=15,
            hour=0, minute=0, second=0
        )

        output = self.client._format_datetime(test_date)

        self.assertEquals(output, '15-06-1977 00:00:00')

        # Attempt parse
        output = self.client._parse_datetime(output)

        # Output should be equal to original
        self.assertEquals(output, test_date)

    def test_from_python(self):
        """ Test _from_python(); Python to PostNL conversion """

        data = {
            'Order': {
                'ExtRef': '1105_900',
                'VerzendDatum': datetime.datetime(
                    year=1977, month=6, day=15,
                    hour=0, minute=0, second=0
                ),
                'Subtotaal': decimal.Decimal('5.00')
            },
        }

        output = self.client._from_python(data)

        self.assertEquals(output, {
            'Order': {
                'ExtRef': u'1105_900',
                'VerzendDatum': u'15-06-1977 00:00:00',
                'Subtotaal': u'5.00'
            },
        })

    def test_to_python(self):
        """ Test _to_python(); PostNL to Python conversion. """

        data = {
            'Order': {
                'ExtRef': u'1105_900',
                'VerzendDatum': u'15-06-1977 00:00:00',
                'Subtotaal': u'5.00'
            }
        }

        output = self.client._to_python(data)

        self.assertEquals(output, {
            'Order': {
                'ExtRef': u'1105_900',
                'VerzendDatum': datetime.datetime(
                    year=1977, month=6, day=15,
                    hour=0, minute=0, second=0
                ),
                'Subtotaal': decimal.Decimal('5.00')
            }
        })

    def test_prepare_order(self):
        """ Test PrepareOrder """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('prepare_order_request.xml')
            )

            return self.read_file('prepare_order_response.xml')

        kwargs = {
            'AangebodenBetaalMethoden': {
                'PrepareOrderBetaalMethode': {
                    'Code': 'IDEAL',
                    'Prijs': '5.00'
                }
            },
            'AangebodenCommunicatieOpties': {
                'PrepareOrderCommunicatieOptie': {
                    'Code': 'NEWS'
                }
            },
            # FIXME: the following is not submitted by SUDS
            # Most probably because it is not properly defined in the WSDL
            # Contact PostNL about this.
            # 'AangebodenOpties': {
            #     'PrepareOrderOptie': {
            #         'Code': 'WRAP',
            #         'Prijs': '2.50'
            #     }
            # },
            # 'AfleverOpties': {
            #     'AfleverOptie': {
            #         'Code': 'PG',
            #         'Kosten': '0.00',
            #         'Toegestaan': True
            #     }
            # },
            'Consument': {
                'ExtRef': 'test@e-id.nl'
            },
            'Contact': {
                'Url': 'http://www.kadowereld.nl/url/contact'
            },
            'Order': {
                'ExtRef': '1105_900',
                'OrderDatum': datetime.datetime(
                    year=2011, month=7, day=21,
                    hour=20, minute=11, second=0
                ),
                'Subtotaal': '125.00',
                'VerzendDatum': datetime.datetime(
                    year=2011, month=7, day=22,
                    hour=20, minute=11, second=0
                ),
                'VerzendKosten': '12.50'
            },
            'Retour': {
                'BeschrijvingUrl': 'http://www.kadowereld.nl/url/beschrijving',
                'PolicyUrl': 'http://www.kadowereld.nl/url/policy',
                'RetourTermijn': 28,
                'StartProcesUrl': 'http://www.kadowereld.nl/url/startproces'
            },
            'Service': {
                'Url': 'http://www.kadowereld.nl/url/service'
            }
        }

        # Execute API call
        with HTTMock(response):
            result = self.client.prepare_order(**kwargs)

        # Assert checkout
        self.assertIn('Checkout', result)

        checkout = result['Checkout']
        self.assertIn('OrderToken', checkout)
        self.assertEquals(
            checkout['OrderToken'], '0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )

        self.assertWebshop(result)

    def test_read_order(self):
        """ Test ReadOrder """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('read_order_request.xml')
            )

            return self.read_file('read_order_response.xml')

        kwargs = {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c'
            }
        }

        # Execute API call
        with HTTMock(response):
            result = self.client.read_order(**kwargs)

        # Assert presence of top level elements
        self.assertIn('BetaalMethode', result)
        self.assertIn('Bezorging', result)
        self.assertIn('CommunicatieOpties', result)
        self.assertIn('Consument', result)
        self.assertIn('Facturatie', result)
        self.assertIn('Opties', result)
        self.assertIn('Order', result)
        self.assertIn('Voorkeuren', result)

        self.assertWebshop(result)

        # Dive into voorkeuren
        voorkeuren = result['Voorkeuren']
        self.assertIn('Bezorging', voorkeuren)

        # Attempt parsing datetime
        self.assertEquals(
            voorkeuren['Bezorging']['Datum'],
            datetime.datetime(
                year=2012, month=4, day=26,
                hour=0, minute=0, second=0
            )
        )

        # FIXME: According to the specs, a ProductType field exists.
        # However, this is not in the XSD and hence causes a validation error.
        # For now, this has been removed from the mock response for now.
        # Eventually, PostNL should be contacted about this.

    def test_confirm_order(self):
        """ Test confirm_order """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('confirm_order_request.xml')
            )

            return self.read_file('confirm_order_response.xml')

        kwargs = {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c'
            },
            'Order': {
                'PaymentTotal': '183.25'
            }
        }

        # Execute API call
        with HTTMock(response):
            result = self.client.confirm_order(**kwargs)

        self.assertWebshop(result)

        # Assert presence of top level elements
        self.assertIn('Order', result)
        order = result['Order']
        self.assertIn('ExtRef', order)

    def test_update_order(self):
        """ Test update_order """

        def response_success(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('update_order_request.xml')
            )

            return self.read_file('update_order_response_success.xml')

        def response_fail(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('update_order_request.xml')
            )

            return self.read_file('update_order_response_fail.xml')

        kwargs = {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c'
            },
            'Order': {
                'ExtRef': 'FDK004',
                'Zending': {
                    'UpdateOrderOrderZending': {
                        'Busstuk': {
                            'UpdateOrderOrderZendingBusstuk': {
                                'Verzonden': '23-08-2011 12:00:00'
                            }
                        },
                        'ExtRef': '642be996-6ab3-4a4c-b7d6-2417a4cee0df',
                        'Pakket': {
                            'UpdateOrderOrderZendingPakket': {
                                'Barcode': '3s123456789',
                                'Postcode': '4131LV'
                            }
                        }
                    }
                }
            }
        }

        # Execute API call
        with HTTMock(response_success):
            result = self.client.update_order(**kwargs)

        # Result should be True
        self.assertTrue(result)

        # Execute API call
        with HTTMock(response_fail):
            result = self.client.update_order(**kwargs)

        # Result should be True
        self.assertFalse(result)

    def test_ping_status(self):
        """ ping_status returns True or False """

        def ok_response(url, request):
            # Assert
            self.assertXMLEqual(
                request.body,
                self.read_file('ping_status_request.xml')
            )
            return self.read_file('ping_status_response_ok.xml')

        def nok_response(url, request):
            return self.read_file('ping_status_response_nok.xml')

        with HTTMock(ok_response):
            self.assertEquals(self.client.ping_status(), True)

        with HTTMock(nok_response):
            self.assertEquals(self.client.ping_status(), False)


class ClientRegressionTests(ClientTests):
    """ Regression tests. """

    def test_from_python_none_date(self):
        """ Regression test for None dates in _from_python. """

        data = {
            'Order': {
                'VerzendDatum': None,
            },
        }

        output = self.client._from_python(data)

        self.assertEquals(output, {
            'Order': {
                'VerzendDatum': None,
            },
        })

    def test_to_python_none_date(self):
        """ Regression test for None dates in _to_python. """

        data = {
            'Order': {
                'VerzendDatum': None,
            }
        }

        output = self.client._to_python(data)

        self.assertEquals(output, {
            'Order': {
                'VerzendDatum': None
            }
        })
