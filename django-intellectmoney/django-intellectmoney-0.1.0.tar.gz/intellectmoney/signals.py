# -*- coding: utf-8 -*-
from django.dispatch import Signal
from datetime import datetime
from annoying.functions import get_object_or_None
from django.core.mail import EmailMessage, EmailMultiAlternatives
from email.MIMEImage import MIMEImage

import settings

result_received = Signal(providing_args=["orderId", "recipientAmount"])
# order_finished = Signal(providing_args=["order"])


def result_received_processor(sender, **kwargs):
    from apps.orders.models import Order, OrderStatusChoices, Ticket, TicketStatus

    if settings.INTELLECTMONEY_DEBUG == u'TST':

        print 'signal works'
        print sender
        print kwargs

        order = get_object_or_None(Order,
            pk=sender.orderId,
        )
    else:
        order = get_object_or_None(Order,
            pk=sender.orderId,
            status__exact=OrderStatusChoices.PAYMENT_PROCESS,
            reserved_til__gte=datetime.now(),
        )

    if order:
        paid_sum = kwargs['recipientAmount']
        if paid_sum != order.total_plus_fee:
            raise ValueError()

        order.confirm()
        order.save()
        order.make_tickets()
        order_finished.send(sender=order, order=order)


# result_received.connect(result_received_processor)
