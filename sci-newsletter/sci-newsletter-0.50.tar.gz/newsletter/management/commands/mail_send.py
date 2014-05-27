#coding: utf-8

from django.core.management.base import BaseCommand, CommandError
from newsletter.models import Job

# Отправить письмо с опр. id без проверки даты
class Command(BaseCommand):
	help = u'Отправляет письмо с указанным id без проверки даты отправки работы. Статус работы должен быть не равен "Отправлено"\n\
Пример: mail_send 3  или mail_send 3 5'

	def handle(self, *args, **options):
		# TODO если нет параметров - сказать об этом
		for job_id in args:
			job = Job.objects.get(pk=job_id)
			print "Отправка письма", job.mail
			job.force_send()