# -*- coding: utf-8 -*-
from annoying.functions import get_object_or_None
from django.conf import settings
from django.core.mail import mail_managers
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.context import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse

from apps.orders.models import Order, OrderStatusChoices

from .models import IntellectMoney
from .signals import result_received
from .forms import ResultUrlForm


RESPONSE_SUCCESS = 'OK'
RESPONSE_FAILURE = 'Bad'

@csrf_exempt
@require_POST
def receive_result(request):
    request.encoding = '1251'
    ip = request.META['REMOTE_ADDR']
    preffix = 'IntellectMoney: '
    info = request.POST

    if settings.INTELLECTMONEY_DEBUG != u'TST' and ip != settings.INTELLECTMONEY_IP:
        subject = u'%sОповещение о платеже с неправильного ip'  % preffix
        mail_managers(subject, message=u'Дата: %s' % info)
        raise Http404
    form = ResultUrlForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        orderId = data['orderId']
        recipientAmount = data['recipientAmount']
        paymentId = data['paymentId']
        invoice = get_object_or_None(IntellectMoney, orderId=orderId)
        if not invoice:
            subject = u'%sОповещение об оплате несуществующего счета #%s' % (
                preffix, paymentId
            )
            mail_managers(subject, message=u'Дата: %s' % data)
            return HttpResponse(RESPONSE_FAILURE)

        invoice.payment_id = paymentId
        invoice.save()

        paymentStatus = data['paymentStatus']
        if paymentStatus in [5, 6, 7]:
            # subject = u'Оплата через intellectmoney #%s' % paymentId
            # if paymentStatus == 6:
            #     message = u'%sОплачен счет %s (ЗАБЛОКИРОВАНО %s руб)' % (
            #        preffix, orderId, recipientAmount,
            #     )
            # else:
            #     message = u'%sОплачен счет %s (%s руб)' % (
            #        preffix, orderId, recipientAmount,
            #     )
            # mail_managers(subject, message=message)
            result_received.send(
                sender=invoice, orderId=orderId, recipientAmount=recipientAmount,
            )
            return HttpResponse(RESPONSE_SUCCESS)
        elif paymentStatus == 3:
            return HttpResponse(RESPONSE_SUCCESS)
        else:
            subject = u'%sПришло оповещение с неожидаемым статусом' % preffix
            mail_managers(subject, message=u'Дата: %s' % info)
        return HttpResponse(RESPONSE_FAILURE)
    else:
        subject = u'%sФорма оповещения платежа: невалидные данные' % preffix
        body = u'Ошибки в форме: %s\n\nДанные:%s' % (unicode(form.errors), info)
        mail_managers(subject, message=body)
        return HttpResponse(RESPONSE_FAILURE, status=400)


@csrf_exempt
def success(request):
    order_id = request.session.get('order_id')
    if not order_id: return redirect('/')
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return redirect('/')
    if order.is_confirmed:
        del request.session['order_id']
        messages.success(request, u'Поздравляем, вы только что приобрели следующие электронные билеты:')
        return redirect('%s?order=%s' % (reverse('ticket_list'), order_id))
    else:
        return render_to_response('message.html',
            {'title': 'Оплата заказа', 'message': u'''
            <img src="/static/img/preloader.gif">
            <br><br>
            Ожидаем подтверждения оплаты...
            ''', 'refresh': True}, context_instance=RequestContext(request))


@csrf_exempt
def fail(request):
    return render_to_response('fail.html',
        context_instance=RequestContext(request)
    )
