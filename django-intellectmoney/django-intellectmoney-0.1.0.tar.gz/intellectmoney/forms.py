# -*- coding: utf-8 -*-
from urllib import urlencode
from .helpers import cheskHashOnReceiveResult, getHashOnRequest
from django import forms
import settings


class _BaseForm(forms.Form):

    eshopId = forms.CharField(initial=settings.INTELLECTMONEY_SHOPID)
    orderId = forms.CharField(max_length=50)

    def clean_eshopId(self):
        eshopId = self.cleaned_data['eshopId']
        if eshopId != settings.INTELLECTMONEY_SHOPID:
            raise forms.ValidationError(u'Неверный eshopId')
        return eshopId


class _BasePaymentForm(_BaseForm):

    CURRENCY_CHOICES = map(lambda x: (x, x), ['RUR', 'TST', 'RUB'])
    serviceName = forms.CharField(label=u'Payment Description', required=False)
    recipientAmount = forms.DecimalField(max_digits=10, decimal_places=2)
    recipientCurrency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial=settings.INTELLECTMONEY_DEBUG
    )
    userName = forms.CharField(max_length=255, required=False)
    userEmail = forms.EmailField(required=False)


class IntellectMoneyForm(_BasePaymentForm):
    """Payment request form."""

    PREFERENCE_CHOICES = [
        ('inner', 'IntellectMoney'),
        ('bankCard', 'Visa/MasterCard'),
        ('exchangers', u'Internet Exchangers'),
        ('terminals', u'Terminals'),
        ('transfers', u'Transfers'),
        ('sms', 'SMS'),
        ('bank', u'Bank'),
        ('yandex', u'Яндекс.Деньги'),
        ('inner,bankCard,exchangers,terminals,bank,transfers,sms', u'All'),
        ('bankCard,exchangers,terminals,bank,transfers,sms', u'All without inner'),
    ]

    successUrl = forms.CharField(
        required=False, max_length=512,
        initial=settings.INTELLECTMONEY_SUCCESS_URL
    )
    failUrl = forms.CharField(
        required=False, max_length=512,
        initial=settings.INTELLECTMONEY_FAIL_URL
    )
    preference = forms.ChoiceField(
        label=u'Payment Method', choices=PREFERENCE_CHOICES, required=False
    )
    expireDate = forms.DateTimeField(required=False)
    holdMode = forms.BooleanField(required=False)
    hash = forms.CharField(required=False)
    user_email = forms.EmailField(required=False)

    def get_redirect_url(self):
        def _initial(name, field):
            val = self.initial.get(name, field.initial)
            if not val:
                return val
            return unicode(val).encode('1251')

        fields = [(name, _initial(name, field))
        for name, field in self.fields.items()
        if _initial(name, field)
        ]

        hash_field = getHashOnRequest(dict(fields))
        fields.append(('hash', hash_field))
        params = urlencode(fields)
        return '{0:s}?{1:s}'.format(settings.INTELLECTMONEY_CLIENT_REDIRECT_URL,params)


class ResultUrlForm(_BasePaymentForm):

    STATUS_CHOICES = [
        (3, u'Создан счет к оплате (СКО) за покупку'),
        (4, u'СКО аннулирован, деньги возвращены пользователю'),
        (7, u'СКО частично оплачен'),
        (5, u'СКО полностью оплачен'),
        (6, u'Cумма заблокирована на СКО, ожидается запрос на списание'),
    ]

    paymentId = forms.CharField(label=u'IntellectMoney Payment ID')
    paymentData = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])
    paymentStatus= forms.TypedChoiceField(choices=STATUS_CHOICES, coerce=int)
    eshopAccount = forms.CharField()
    hash = forms.CharField()
    secretKey = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ResultUrlForm, self).__init__(*args, **kwargs)
        if settings.INTELLECTMONEY_SEND_SECRETKEY:
            self.fields['hash'].required = False
            self.fields['secretKey'].required = True
        else:
            self.fields['hash'].required = True
            self.fields['secretKey'].required = False

    def clean_secretKey(self):
        secretKey = self.cleaned_data['secretKey']
        if settings.INTELLECTMONEY_SEND_SECRETKEY:
            if secretKey != settings.INTELLECTMONEY_SECRETKEY:
                raise forms.ValidationError(u'Неверное значение')
        return secretKey

    def clean(self):
        data = self.cleaned_data
        if not settings.INTELLECTMONEY_SEND_SECRETKEY:
            if not cheskHashOnReceiveResult(data):
                raise forms.ValidationError(u'Неверный hash')
        return data


class AcceptingForm(_BaseForm):

    ACTION_CHOICES = [
        ('Refund', 'Refund'),
        ('ToPaid', 'ToPaid')
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES)
    secretKey = forms.CharField()
