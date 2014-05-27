#coding: utf-8

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from newsletter.models import Job, MAIL_STATE_DRAFT, MAIL_STATE_SENT,  MAIL_STATE_READY
import datetime
from datetime import timedelta

# Показать все неотправленные, все отправленные за всё время, за указанный период.
class Command(BaseCommand):
	help = u'Может показать все неотправленные письма, отправленные за всё время, за некоторые период\n\
	Параметры: --sended, --not_sended --time'
	option_list = BaseCommand.option_list + (
		make_option('--sended',
			action='store_true',
			dest='sended',
			default=False,
			help=u'Показывает все отправленные письма'),
		make_option('--not_sended',
			action='store_true',
			dest='not_sended',
			default=False,
			help=u'Показывает все неотправленные письма'),
		make_option('--time',
			action='store_true',
			dest='time',
			default=False,
			help=u'Письма за последние N дней'),
	)

	def handle(self, *args, **options):
		if options['sended']:
			print u"Отправленые письма:"
			for job in Job.objects.all().filter(state=MAIL_STATE_SENT):
				print job

		if options['not_sended']:
			print u"Неотправленые письма:"
			for job in Job.objects.all().filter(state__lt=MAIL_STATE_SENT):
				print job

		if options['time']:
			days = 30
			print u"Письма за период", days, u"дней"
			for job in Job.objects.all().filter(send_date__range=(datetime.date.today() - timedelta(days=days),datetime.date.today())):
				print job