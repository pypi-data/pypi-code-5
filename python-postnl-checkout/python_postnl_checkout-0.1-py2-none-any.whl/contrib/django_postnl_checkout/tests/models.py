import datetime
import decimal

from django.test import TestCase
from django.core.cache import cache

from httmock import HTTMock

from django_dynamic_fixture import G, N

from postnl_checkout.tests.base import PostNLTestMixin

from ..models import Order


class OrderTests(PostNLTestMixin, TestCase):
    """ Tests for Order model. """
    maxDiff = None

    def setUp(self):
        super(OrderTests, self).setUp()

        self.order_datum = datetime.datetime(
            year=2011, month=7, day=21,
            hour=20, minute=11, second=0
        )

        self.verzend_datum = datetime.datetime(
            year=2011, month=7, day=22,
            hour=20, minute=11, second=0
        )

    def test_save(self):
        """ Test saving an Order model. """
        instance = N(Order)
        instance.clean()
        instance.save()

    def test_prepare_order(self):
        """ Test prepare_order class method. """

        # Setup mock response
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
                'OrderDatum': self.order_datum,
                'Subtotaal': '125.00',
                'VerzendDatum': self.verzend_datum,
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
            instance = Order.prepare_order(**kwargs)

        # Assert model field values
        self.assertTrue(instance.pk)

        self.assertEquals(
            instance.order_token, '0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )
        self.assertEquals(
            instance.order_ext_ref, '1105_900'
        )
        self.assertEquals(
            instance.order_date, self.order_datum
        )

        # Assert JSON values
        self.assertEquals(instance.prepare_order_request, kwargs)
        self.assertEquals(instance.prepare_order_response, {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c',
                'Url': (
                    'http://tpppm-test.e-id.nl/Orders/OrderCheckout'
                    '?token=0cfb4be2-47cf-4eac-865c-d66657953d5c'
                )
            },
            'Webshop': {
                'IntRef': 'a0713e4083a049a996c302f48bb3f535'
            }
        })

    def test_read_order(self):
        """ Test read_order method. """

        # Setup mock response
        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('read_order_request.xml')
            )

            return self.read_file('read_order_response.xml')

        instance = G(
            Order,
            order_token='0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )

        # Read order data
        with HTTMock(response):
            new_instance = instance.read_order()

        response_data = new_instance.read_order_response

        self.assertTrue(response_data)

        self.assertEquals(response_data, {
            'Voorkeuren': {
                'Bezorging': {
                    'Tijdvak': {
                        'Start': u'10:30',
                        'Eind': u'08:30'
                    },
                    'Datum': datetime.datetime(2012, 4, 26, 0, 0)
                }
            },
            'Consument': {
                'GeboorteDatum': datetime.datetime(1977, 6, 15, 0, 0),
                'ExtRef': u'jjansen',
                'TelefoonNummer': u'06-12345678',
                'Email': u'j.jansen@e-id.nl'
            },
            'Facturatie': {
                'Adres': {
                    'Huisnummer': u'1',
                    'Initialen': u'J',
                    'Geslacht': u'Meneer',
                    'Deurcode': None,
                    'Gebruik': u'P',
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': u'Jansen',
                    'Afdeling': None,
                    'Regio': None,
                    'Land': u'NL',
                    'Wijk': None,
                    'Postcode': u'4131LV',
                    'Straat': 'Lage Biezenweg',
                    'Bedrijf': None,
                    'Plaats': u'Vianen',
                    'Tussenvoegsel': None,
                    'Voornaam': u'Jan',
                    'HuisnummerExt': None
                }
            },
            'Webshop': {
                'IntRef': u'a0713e4083a049a996c302f48bb3f535'
            },
            'CommunicatieOpties': {
                'ReadOrderResponseCommunicatieOptie': [
                    {
                        'Text': u'Do not deliver to neighbours',
                        'Code': u'REMARK'
                    }
                ]
            },
            'Bezorging': {
                'ServicePunt': {
                    'Huisnummer': None,
                    'Initialen': None,
                    'Geslacht': None,
                    'Deurcode': None,
                    'Gebruik': None,
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': None,
                    'Afdeling': None,
                    'Regio': None,
                    'Land': None,
                    'Wijk': None,
                    'Postcode': None,
                    'Straat': None,
                    'Bedrijf': None,
                    'Plaats': None,
                    'Tussenvoegsel': None,
                    'Voornaam': None,
                    'HuisnummerExt': None
                },
                'Geadresseerde': {
                    'Huisnummer': u'1',
                    'Initialen': u'J',
                    'Geslacht': u'Meneer',
                    'Deurcode': None,
                    'Gebruik': u'Z',
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': u'Janssen',
                    'Afdeling': None,
                    'Regio': None,
                    'Land': u'NL',
                    'Wijk': None,
                    'Postcode': u'4131LV',
                    'Straat': u'Lage Biezenweg ',
                    'Bedrijf': u'E-ID',
                    'Plaats': u'Vianen',
                    'Tussenvoegsel': None,
                    'Voornaam': u'Jan',
                    'HuisnummerExt': None
                }
            },
            'Opties': {
                'ReadOrderResponseOpties': [
                    {
                        'Text': u'Congratulat ions with your new foobar!',
                        'Code': u'CARD',
                        'Prijs': decimal.Decimal('2.00')
                    }
                ]
            },
            'Order': {
                'ExtRef': u'15200_001'
            },
            'BetaalMethode': {
                'Optie': u'0021',
                'Code': u'IDEAL',
                'Prijs': decimal.Decimal('0.00')
            }
        })

    def test_confirm_order(self):
        """ Test confirm_order """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('confirm_order_request.xml')
            )

            return self.read_file('confirm_order_response.xml')

        kwargs = {
            'Order': {
                'PaymentTotal': decimal.Decimal('183.25')
            }
        }

        instance = G(
            Order,
            order_token='0cfb4be2-47cf-4eac-865c-d66657953d5c',
            order_ext_ref='1105_900'
        )

        # Execute API call
        with HTTMock(response):
            instance.confirm_order(**kwargs)

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

        instance = G(
            Order,
            order_token='0cfb4be2-47cf-4eac-865c-d66657953d5c',
            order_ext_ref='1105_900'
        )

        # Make call fail
        with HTTMock(response_fail):
            self.assertRaises(
                Exception, lambda: instance.update_order(**kwargs)
            )

        # Make call pass
        with HTTMock(response_success):
            response = instance.update_order(**kwargs)

        self.assertTrue(response)

        # Make sure the requested stuff is saved
        self.assertEquals(
            instance.update_order_request, {
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
        )

    def test_ping_status(self):
        """ Test ping_status """

        instance = G(Order)

        self.response_called = 0

        def ok_response(url, request):
            # Assert
            self.assertXMLEqual(
                request.body,
                self.read_file('ping_status_request.xml')
            )

            self.response_called += 1

            return self.read_file('ping_status_response_ok.xml')

        def nok_response(url, request):
            return self.read_file('ping_status_response_nok.xml')

        with HTTMock(ok_response):
            self.assertEquals(instance.ping_status(), True)

        self.assertEquals(self.response_called, 1)

        # Repeated call should not cause the response to be called
        with HTTMock(ok_response):
            self.assertEquals(instance.ping_status(), True)

        self.assertEquals(self.response_called, 1)

        # Clear cache
        cache.clear()

        with HTTMock(nok_response):
            self.assertEquals(instance.ping_status(), False)
