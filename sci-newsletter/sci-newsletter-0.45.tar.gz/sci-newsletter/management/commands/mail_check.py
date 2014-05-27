#coding: utf-8

from django.core.management.base import BaseCommand, CommandError
from newsletter.models import Job, MAIL_STATE_READY

# вызывает check_schedule
class Command(BaseCommand):
	help = u'Проверяет все работы со состоянием "Ждет отправки", и если дата отправления наступила - отправляет их'

	def handle(self, *args, **options):
		print u"Проверка писем, готовых к отправке..."
		Job.check_schedule()