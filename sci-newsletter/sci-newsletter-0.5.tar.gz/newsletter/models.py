# coding: utf-8
from django.db import models
from ckeditor.fields import RichTextField
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.conf import settings
from django.template import Template, Context
import django.template

# Необходим для корректного преобразования текста CKEditor в HTML-текст
from django.utils.safestring import mark_safe  
from dateutil.relativedelta import relativedelta
import datetime

# -=-=-=-=- sci-newsletter models: -=-=-=-=-
MAIL_STATE_DRAFT = 0
MAIL_STATE_READY = 1
MAIL_STATE_SENT = 2

MAIL_STATE_DRAFT_TUPLE = (MAIL_STATE_DRAFT, u'Черновик')
MAIL_STATE_READY_TUPLE = (MAIL_STATE_READY, u'К отправке')
MAIL_STATE_SENT_TUPLE = (MAIL_STATE_SENT, u'Отправлено')

ALL_MAIL_STATES = (
	MAIL_STATE_DRAFT_TUPLE,
	MAIL_STATE_READY_TUPLE,
	MAIL_STATE_SENT_TUPLE,
)

NOT_SENT_MAIL_STATES = (
	MAIL_STATE_DRAFT_TUPLE,
	MAIL_STATE_READY_TUPLE,
)

SENT_MAIL_STATES = (
	MAIL_STATE_SENT_TUPLE,
)

RECIEVERS_SUBSCRIBED = '0'
RECIEVERS_ALL = '1'

RECIEVERS_STATE = (
	(RECIEVERS_SUBSCRIBED, u'Подписанные на рассылку'),
	(RECIEVERS_ALL, u'Все пользователи'),
)

NEWSLETTER_MONTLY = '0'
NEWSLETTER_PERIOD = '1'

NEWSLETTER_TYPE = (
	(NEWSLETTER_MONTLY, u'День N каждого месяца'),
	(NEWSLETTER_PERIOD, u'Каждые N дней'),
)

def get_feed_items(since=None, till=None):
	filters = Q()
	if since:
		filters &= Q(datetime__gt=since)
	if till:
		filters &= Q(datetime__lte=till)

	print "WARNING: NO IMPLEMENTATION GET_FEED_ITEMS"
	return []

class NewsletterSettings(models.Model):
	newsletter_type = models.CharField(verbose_name=u'Периодичность рассылки', max_length=125, choices=NEWSLETTER_TYPE, default=NEWSLETTER_MONTLY)
	day = models.IntegerField(verbose_name=u'N:', default=7, validators=[MinValueValidator(1), MaxValueValidator(28)])

	def __unicode__(self):
		return NEWSLETTER_TYPE[int(self.newsletter_type)][1] + ", N=" + str(self.day)

class Job(models.Model):
	send_date = models.DateField(verbose_name=u'Дата отправки письма', auto_now=False, auto_now_add=False)
	state = models.DecimalField(max_digits=1, decimal_places=0, choices=ALL_MAIL_STATES, default=MAIL_STATE_DRAFT, verbose_name=u'Статус рассылки')
	mail = models.ForeignKey('newsletter.Mail', related_name="mails", verbose_name=u'Письмо')
	recievers = models.CharField(verbose_name=u'Получатели', max_length=125, choices=RECIEVERS_STATE, default=RECIEVERS_SUBSCRIBED)

	def send(self):
		"""
		Отправляет письмо при условии, если состояние работы = STATE_READY и время рассылки >= текущей даты.
		При успешной отправке меняет статус на STATE_SENT
		Возвращает истину, если удалось отправить письмо
		"""
		# DEBUG Print
		print u"Имя шаблона:", self.mail.template.name
		if (self.mail.template.name == u'Ежемесячная рассылка'):
			self.make()

		if self.check():
			if (self.mail.text == ''):
				print u"Письмо пустое. Перенос даты рассылки..."
				self.send_date = Job.get_next_send_date()
				self.save()
				self.make()
				return False

			if self.force_send():
				# Если отправилась ежемесячная рассылка, создаем новую
				if (self.mail.template.name == u"Ежемесячная рассылка"):
					print u"Создание новой ежемесячной рассылки. Прошлая была отправлена..."
					template = MailTemplate.objects.get(name=u"Ежемесячная рассылка")
					mail_new = Mail(subject="", text="", template=template)
					mail_new.save()

					# Отсчет даты идет от текущей даты, когда было отправлено письмо
					new_send_date = Job.get_next_send_date()
					print "Дата следующей ежемесячной рассылки:", new_send_date
					job_new = Job(send_date=new_send_date, state=MAIL_STATE_DRAFT, mail=mail_new, recievers=RECIEVERS_SUBSCRIBED)
					job_new.save()
					job_new.make()
					job_new.save()
				return True
			return False
		return False

	def force_send(self):
		"""
		Отправляет письмо без проверки на дату. Не отсылает при статусе = 'Отослан'
		"""
		log_file = '/tmp/feed.log'

		connection = get_connection()

		messages = []
		subj = self.mail.subject
		text = self.get_html()
		src = settings.EMAIL_HOST_USER

		for email in self.get_recievers_list():
			message = EmailMultiAlternatives(subj, text, src, [email])
			message.attach_alternative(text, 'text/html')
			messages.append(message)

		if (not self.state == MAIL_STATE_SENT):
			try:
				count = connection.send_messages(messages)
				open(log_file, 'a').write( str(datetime.date.today()) + ' рассылка была успешно отправлена. Писем: %i\n' % count)
				self.state = MAIL_STATE_SENT
				self.save()
				return True
			except Exception:
				open(log_file, 'a').write( str(datetime.date.today()) + " рассылка не отправлена: произошла ошибка в отправке рассылки.\n")
				return False
		open(log_file, 'a').write( str(datetime.date.today()) + " рассылка не отправлена: оно уже было ранее отправлена.\n")
		return False

	def check(self):
		if (datetime.date.today() >= self.send_date):
			if (self.state == MAIL_STATE_READY):
				print u"Работа '", self, u"' готова к отправке..."
				return True
			print u"Письмо не готово к отправке. Письмо не находится в состоянии 'Ждет отправки'. Работа: '", self, "'"
			return False
		print u"Письмо не готово к отправке. Дата отправки еще не настала. Работа: '", self, "'"
		return False

	# def get_recievers(self):
	# 	"""
	# 	Возвращает список почтовых адресов получателей в зависимости от текущей работы (состояния получателей)
	# 	---Переписана под scibib
	# 	"""
	# 	# TODO: Глянуть Q объект джанговский
	# 	emails = []

	# 	print "WARINGN: NO IMPLEMENTATION GET_RECIEVERS"
	# 	return emails

	# для аджакса
	@staticmethod
	def get_recievers_list(id_recievers):
		"""
		Возвращает список получателей в формате ФИО <почта>
		"""
		users = []

		print "WARNING: NO IMPLEMENTATION GET_RECIEVERS_LIST"
		return users

	def get_html(self):
		"""
		Возвращает полный html-текст письма, который отправился бы, если бы письмо было бы отправлено сейчас
		Создает html-текст из текста письма и шаблона письма
		"""
		print "WARNING: NO IMPLEMENTATION GET_HTML"

	def make(self):
		"""
		Генерирует письмо на текущий момент. Генерируется заголовок письма, измененные источники (новости),
		обновляетя состояние работы
		***Осторожно*** генерация заменяет собой те данные, которые уже были на месте текста и заголовка письма!
		"""
		# Генерация перезаписывает письмо
		# Если письмо уже отправлено - запретить генерацию письма
		if (self.state == MAIL_STATE_SENT):
			return
		self.state = MAIL_STATE_READY
		self.save()

		self.mail.subject = u"Рассылка от " + str(self.send_date.strftime(settings.TIME_FORMAT))

		# получение объектов:
		# Данные берутся с момента последней рассылки
		since = self.get_last_send_date()
		till = datetime.date.today() + datetime.timedelta(days=1)

		feed_items = get_feed_items(since, till)
		template = django.template.loader.get_template('newsletter_feed.txt')
		context = django.template.Context({'items': feed_items})
		txt = template.render(context)

		self.mail.text = txt
		self.mail.save()

	def get_last_send_date(self):
		"""Возвращает дату отправки последней ежемесячной рассылки.
		Если рассылок не было, возвращает дату месяц назад от текущей даты рассылки"""
		try: 
			result = Job.objects.filter(state=MAIL_STATE_SENT, mail__template__name__startswith='Ежемесячная').order_by('-send_date')[0].send_date
		except IndexError:
			now = datetime.date.today()
			result = self.send_date - relativedelta(months=1)
		return result

	@staticmethod
	def get_next_send_date():
		"""Возвращает дату отправки следующей рассылки, согласно настройкам рассылки"""
		nl_settings = NewsletterSettings.objects.all()[0]
		N = nl_settings.day
		if (nl_settings.newsletter_type == NEWSLETTER_PERIOD):
			new_send_date = datetime.date.today() + datetime.timedelta(days=N)
		elif (nl_settings.newsletter_type == NEWSLETTER_MONTLY):
			now = datetime.date.today()
			new_send_date = datetime.date(now.year, now.month, N) + relativedelta(months=1)
		return new_send_date

	@staticmethod
	def check_schedule():
		"""
		Команда для Cron'а. Проверяет все работы, если время пришло и статус работы READY,
		делает рассылку этой работы. 
		A new feed will be created, if feed list is empty	
		Не отправляет пустые письма.
		"""
		feed = Job.objects.filter(mail__template__name__startswith='Ежемесячная')
		if (len(feed) == 0):
			Job.create_feed()

		for job in Job.objects.all().filter(state=MAIL_STATE_READY).order_by("send_date"):
			job.send()

	@staticmethod
	def create_feed():
		"""
		Создает новую новостную рассылку и возвращает её id
		"""
		print "Creating new newsletter feed..."
		template = MailTemplate.objects.get(name=u"Ежемесячная рассылка")
		mail_new = Mail(subject="", text="", template=template)
		mail_new.save()
		job_new = Job(send_date=(Job.get_next_send_date()), state=MAIL_STATE_READY, mail=mail_new, recievers=RECIEVERS_SUBSCRIBED)
		job_new.save()
		job_pk = job_new.id
		job_new.make()
		return job_pk
	
	# TODO: Привести в порядок unicode функции
	def __unicode__(self):
		return self.mail.template.name + u" №"+ str(self.pk) + ', ' + self.mail.__unicode__() + '. ' + ALL_MAIL_STATES[int(self.state)][1]

class Mail(models.Model):
	subject = models.CharField(verbose_name=u'Тема письма', max_length=125)
	text = RichTextField(verbose_name=u'Текст письма', config_name='default')
	template = models.ForeignKey('newsletter.MailTemplate', related_name="templates", verbose_name=u'Шаблон для письма')

	def __unicode__(self):
		return self.subject

class MailTemplate(models.Model):
	name = models.CharField(verbose_name=u'Название шаблона', max_length=125)
	template = models.TextField(verbose_name=u'Текст шаблона')

	def __unicode__(self):
		return self.name