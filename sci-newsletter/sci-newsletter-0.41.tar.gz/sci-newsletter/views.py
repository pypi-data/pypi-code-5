# coding: utf-8
from django.core.context_processors import csrf
from django.template import Template, Context
from django.conf.global_settings import TIME_FORMAT
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from models import *
from django.contrib.auth.decorators import permission_required
import json
from forms import MailForm, JobForm, NewsletterSettingsForm, CKEditorForm
import datetime

from django.core.mail import send_mail

# TODO Ограничить доступ к страницам рассылки

def saveForms(job_pk, formsData):
	"""
	Сохраняет данные форм со страницы в работу с ключем job_pk
	Страница должна быть с двумя формами: mail и job
	formsData - заполненный кортеж (fJob, fMail)
	"""
	job = Job.objects.get(pk=job_pk)
	job.send_date = formsData[0].cleaned_data['send_date']
	job.state = formsData[0].cleaned_data['state']
	job.recievers = formsData[0].cleaned_data['recievers']
	job.save()

	job.mail.text = formsData[1].cleaned_data['text']
	job.mail.subject = formsData[1].cleaned_data['subject']
	job.mail.save()

	return

# TODO: файлы шаблонов лежат в bib/templates/newsletter...
def job(request, job_pk):
	ctx = {}

	# Получаем саму работу
	ctx.update({'job_pk': job_pk})
	job = Job.objects.get(pk=job_pk)
	newsletterSettings = NewsletterSettings.objects.all()[0]

	ctx.update(csrf(request))

	# Если принимаем форму:
	if request.method == 'POST':
		fJob = JobForm(request.POST)
		fMail = MailForm(request.POST)
		fSettings = NewsletterSettingsForm(request.POST)
		formsData = (fJob, fMail)

		# Сохранение настроек рассылки, если они были переданы
		if fSettings.is_valid():
			if 'save' in request.POST:
				newsletterSettings.newsletter_type = fSettings.cleaned_data['newsletter_type']
				newsletterSettings.day = fSettings.cleaned_data['day']
				newsletterSettings.save()
				print "Настройки рассылки сохранены..."

		if fJob.is_valid() and fMail.is_valid():
			if 'send' in request.POST:
				# TODO необходимо сохранять письмо и после уже отправлять
				saveForms(job_pk, formsData)
 				if (job.send()):
					return redirect( reverse('job_list') )
				else:
					# Нет информации о том, что письмо не было отправлено и почему
					return redirect( reverse('job', args=[job_pk]) )

			if 'create' in request.POST:
				mail_new = Mail(subject=fMail.cleaned_data['subject'], text=fMail.cleaned_data['text'], template=fMail.cleaned_data['template'])
				mail_new.save()
				job_new = Job(send_date=fJob.cleaned_data['send_date'], state=fJob.cleaned_data['state'], mail=mail_new, recievers=fJob.cleaned_data['recievers'])
				job_new.save()
				job_pk = job_new.id
				return redirect( reverse('job', args=[job_pk]) )

			if 'save' in request.POST:
				saveForms(job_pk, formsData)
				return redirect( reverse('job', args=[job_pk]) )

			if 'preview' in request.POST:
				saveForms(job_pk, formsData)
				return redirect( reverse('preview', args=[job_pk]) )

		# При этих действиях не нужна валиация формы:
		if 'update' in request.POST:
			job.make()
			return redirect( reverse('job', args=[job_pk]) )

		if 'delete' in request.POST:
			job.delete()
			return redirect( reverse('job_list') )

	# Если посылаем начальную форму
	else:
		# Если загружается неотосланная рассылка - обновялем её и добавляем настройки рассылки:
		if (job.mail.template.name == u'Ежемесячная рассылка' and not job.state == MAIL_STATE_SENT):
			fSettings = NewsletterSettingsForm(initial={'newsletter_type': newsletterSettings.newsletter_type, 'day': newsletterSettings.day })
			ctx.update({'formSettings': fSettings})
			job.make()

		fJob = JobForm(initial={'send_date': job.send_date.strftime(settings.TIME_FORMAT), 'state': job.state, 'mail': job.mail, 'recievers': job.recievers })
		fMail = MailForm(initial={'subject': job.mail.subject, 'text': job.mail.text, 'template': job.mail.template })

		if job.state == MAIL_STATE_SENT:
			fJob.fields['state'].choices = SENT_MAIL_STATES
		else:
			fJob.fields['state'].choices = NOT_SENT_MAIL_STATES

	ctx.update({'formJob': fJob})
	ctx.update({'formMail': fMail})
	ctx.update({'emails': ", ".join( job.get_recievers_list(job.recievers) )})

	if (job.mail.template.name == u'Ежемесячная рассылка'):
		ctx.update({'is_feed': True })
	else:
		ctx.update({'is_feed': False })

	return render(request, 'newsletter/main.html', ctx)

def job_preview(request, job_pk):
	job = Job.objects.get(pk=job_pk)

	ctx = {}
	ctx.update({'previewText': job.get_html()})
	ctx.update({'job_pk': job_pk })
	ctx.update({'recievers': ", ".join( job.get_recievers_list(job.recievers) )})
	ctx.update({'send_date': job.send_date.strftime(settings.TIME_FORMAT)})
	ctx.update(csrf(request))
	# not_sent - показывать ли кнопку "редактировать" в предпросмотре и список получателей.
	if (job.state == MAIL_STATE_SENT):
		ctx.update({'not_sent': False })
	else:
		ctx.update({'not_sent': True })

	ckeForm = CKEditorForm(initial={'text': ctx['previewText'] })
	ctx.update({'ckeForm': ckeForm})
	return render(request, 'newsletter/preview.html', ctx)

def job_preview_last(request):
	job_sent_list = Job.objects.all().filter(state=MAIL_STATE_SENT).order_by('-send_date')
	if len(job_sent_list) >= 1:
		job = job_sent_list[0]
	else:
		return redirect(reverse('job_list'))
	return redirect( reverse('preview', args=[job.pk]) )

def job_list(request):
	ctx = {}
	# Какое условие фильтра != (?)
	jobs = Job.objects.all().filter(state__lt=MAIL_STATE_SENT).order_by('send_date')
	ctx.update({'jobs': jobs})
	return render(request, 'newsletter/jobs.html', ctx)

def new_job(request):
	template = MailTemplate.objects.get(name=u"Пользовательское письмо")
	mail_new = Mail(subject="", text="", template=template)
	mail_new.save()
	job_new = Job(send_date=datetime.date.today(), state=MAIL_STATE_DRAFT, mail=mail_new, recievers=RECIEVERS_SUBSCRIBED)
	job_new.save()
	job_pk = job_new.id
	return redirect(reverse('job', args=[job_pk]) )

def feed(request):
	"""Направляет на страницу текущей ежемесячной рассылки. Если рассылок нет - создает ее"""
	feed = Job.objects.filter(mail__template__name__startswith='Ежемесячная', state__lt=MAIL_STATE_SENT)
	if (len(feed) == 0):
		job_pk = Job.create_feed()	
		return redirect( reverse('job', args=[job_pk]) )
	else:
		job_pk = feed[0].id
		return redirect( reverse('job', args=[job_pk]) )

def archive(request):
	ctx = {}
	jobs = Job.objects.all().filter(state=MAIL_STATE_SENT).order_by('-send_date')
	ctx.update({'jobs': jobs })
	ctx.update({'archive': True })
	return render(request, 'newsletter/jobs.html', ctx)

# Ajax:
def get_recievers(request):
	rec = request.GET['rec']
	response = Job.get_recievers_list(rec)
	content = json.dumps(response)
	return HttpResponse(content, mimetype='application/javascript; charset=utf8')