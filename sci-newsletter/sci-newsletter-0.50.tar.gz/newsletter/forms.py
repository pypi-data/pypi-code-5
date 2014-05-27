# coding: utf-8

from django import forms
from django.db import models
from django.forms import ModelForm, ModelMultipleChoiceField
from models import Job, Mail, NewsletterSettings, ALL_MAIL_STATES, RECIEVERS_STATE
from ckeditor.widgets import CKEditorWidget

# from bib import widgets

class JobForm(ModelForm):
	send_date = forms.DateTimeField(label=u'Следующая отправка', input_formats=['%d.%m.%Y'])
	# send_date = forms.DateTimeField(label=u'Следующая отправка', widget=widgets.DatePicker)
	class Meta:
		model = Job
		fields = ['send_date', 'state', 'recievers']
		# widgets = {
		# 	'state': widgets.RadioButtonPicker,
		# 	'recievers': widgets.RadioButtonPicker,
		# }

	def __init__(self, *args, **kwargs):
		super(JobForm, self).__init__(*args, **kwargs)
		self.fields['state'].widget.attrs['class'] = 'state'

class MailForm(ModelForm):
	class Meta:
		model = Mail
		fields = ['subject', 'text']

class NewsletterSettingsForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(NewsletterSettingsForm, self).__init__(*args, **kwargs)
		for name, field in self.fields.items():
			field.widget.attrs['display'] = 'inline-block'
	class Meta:
		model = NewsletterSettings
		fields = ['newsletter_type', 'day']

class CKEditorForm(forms.Form):
	text = forms.CharField(label=u'', widget=CKEditorWidget())