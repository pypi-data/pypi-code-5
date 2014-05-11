#coding:utf-8
from annoying.functions import get_object_or_None
from django.db import models
import datetime

from apps.orders.models import Order

class IntellectMoney(models.Model):
    created = models.DateTimeField(editable=True, default=datetime.datetime.now)
    orderId = models.CharField(unique=True, editable=True, max_length=255, db_index=True)
    order = models.OneToOneField(Order, blank=True, null=True)
    payment_id = models.CharField(blank=True, editable=True, max_length=255)

    class Meta:
        verbose_name = "Intellectmoney"
        verbose_name_plural = "Invoices"
        ordering = ['-created']

    def __unicode__(self):
        return u'{0} {1} {2}'.format(self.id, self.orderId, self.created)

