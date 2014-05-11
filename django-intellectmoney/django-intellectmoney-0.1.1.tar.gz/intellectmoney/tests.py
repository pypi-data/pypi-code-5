# -*- coding:utf-8 -*-
from django import test
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client
from .forms import IntellectMoneyForm, ResultUrlForm
from .helpers import getHashOnReceiveResult
# Not avaliable in Django 1.3 yet
# from django.test.utils import override_settings


class IntellectMoneyTest(test.TestCase):

    def setUp(self):
        self.url = reverse('intellectmoney-result')
        self.client = Client(REMOTE_ADDR=settings.INTELLECTMONEY_IP)
        self.data = {
            'serviceName': u'Тестовая оплата',
            'recipientAmount': '12222.32', 'recipientCurrency': 'RUR',
            'userName': '3434', 'email': 'test@example.com',
            'eshopId': settings.INTELLECTMONEY_SHOPID, 'paymentId': '323',
            'secretKey': settings.INTELLECTMONEY_SECRETKEY, 'orderId': '434000',
            'paymentStatus': 7, 'eshopAccount': '2212',
            'paymentData': '2011-01-01 01:01:01',
        }

    def tearDown(self):
        del self.data

    def testRequestForm(self):
        data = {
            'preference': 'bankCard', 'serviceName': u'Тестовый Платеж',
            'recipientAmount': '10000000.06', 'recipientCurrency': 'RUR',
            'userName': 'Test User Name', 'email': 'roman@netangels.ru',
            'orderId': 15, 'successUrl': '/dsdsd/', 'failUrl': '/dsdsda/',
            'eshopId': settings.INTELLECTMONEY_SHOPID
        }
        form = IntellectMoneyForm(data)
        form.is_valid()
        self.assertTrue(form.is_valid())

    def testResultBadIp(self):
        client = Client(REMOTE_ADDR='992.993.994.995')
        response = client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self._assertTicketExists()

    # @override_settings(INTELLECTMONEY_SEND_SECRETKEY=False)
    def testResultBadShopId(self):
        settings.INTELLECTMONEY_SEND_SECRETKEY = False
        data = self.data
        data['eshopId'] = '%s1' % settings.INTELLECTMONEY_SHOPID
        data['hash'] = 1
        client = self.client
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        form = ResultUrlForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertTrue('eshopId' in form.errors)
        self._assertTicketExists()

    # @override_settings(INTELLECTMONEY_SEND_SECRETKEY=False)
    def testResultBadHash(self):
        settings.INTELLECTMONEY_SEND_SECRETKEY = False
        data = self.data
        hash = getHashOnReceiveResult(data)
        data['hash'] = hash + '343'
        client = self.client
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        form = ResultUrlForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('__all__' in form.errors)
        self.assertTrue('hash' in unicode(form.errors['__all__']))
        self._assertTicketExists()

    # @override_settings(INTELLECTMONEY_SEND_SECRETKEY=True)
    def testResultBadSecretKey(self):
        settings.INTELLECTMONEY_SEND_SECRETKEY = True
        data = self.data
        data['secretKey'] = data['secretKey'] + '343'
        client = self.client
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        form = ResultUrlForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('secretKey' in form.errors)
        self._assertTicketExists()

    def testResultBadInvoiceDoesNotFound(self):
        data = self.data
        hash = getHashOnReceiveResult(data)
        data['hash'] = hash
        client = self.client
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = ResultUrlForm(data)
        self.assertTrue(form.is_valid())
        #TODO: Существование счетов
        self.assertTrue(invoices.exists())
        #TODO: Существование платежей
        self.assertTrue(payments.exists())
        self._assertTicketExists()

    def testResultWithUnknownStatus(self):
        data = self.data
        data['paymentStatus'] = 4
        hash = getHashOnReceiveResult(data)
        data['hash'] = hash
        client = self.client
        response = client.post(self.url, data)
        form = ResultUrlForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)
        #TODO: Существование платежей
        self.assertFalse(payments.exists())
        self._assertTicketExists()

    def testResult(self):
        amount = '10.11'
        data = self.data
        data['orderId'] = inv.id
        hash = getHashOnReceiveResult(data)
        data['hash'] = hash
        client = self.client
        response = client.post(self.url, data)
        form = ResultUrlForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)
        orderId = data['orderId']
        recipientAmount = data['recipientAmount']
        self.assertTrue(payments.exists())
        payment = payments[0]
        self.assertTrue(invoices.exists())

    def testResultAlreadyHavePaymentStatus(self):
        data = self.data
        data['orderId'] = inv.id
        hash = getHashOnReceiveResult(data)
        data['hash'] = hash
        client = self.client
        response = client.post(self.url, data)
        form = ResultUrlForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(payments.exists())
        self._assertTicketExists()

    def testResultBadFormData(self):
        data = self.data
        del data['eshopAccount']
        client = self.client
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        form = ResultUrlForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('eshopAccount' in form.errors)
        self._assertTicketExists()

