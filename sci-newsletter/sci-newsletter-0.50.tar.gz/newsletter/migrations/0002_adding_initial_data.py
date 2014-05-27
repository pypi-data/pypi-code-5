# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from newsletter.models import NEWSLETTER_MONTLY

class Migration(DataMigration):

	def forwards(self, orm):
		"Write your forwards methods here."
		
		templateText="""
<b>Доброго времени суток!</b>
<br>
<i>На нашем сайте произошли следующие изменения:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта SciBib</i>
"""
		feedTemplate = orm['newsletter.mailtemplate'].objects.create(name='Ежемесячная рассылка', template=templateText)
		feedTemplate.save()

		templateText="""
<b>Доброго времени суток!</b>
<br>
<i>У нас есть для вас следующая информация:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта SciBib</i>
"""
		mailTemplate = orm['newsletter.mailtemplate'].objects.create(name='Пользовательское письмо', template=templateText)
		mailTemplate.save()

		feedSettings = orm['newsletter.newslettersettings'].objects.create(newsletter_type=NEWSLETTER_MONTLY, day = 12)
		feedSettings.save()

	def backwards(self, orm):
		"Write your backwards methods here."
		orm['newsletter.mailtemplate'].objects.get(name="Ежемесячная рассылка").delete()
		orm['newsletter.mailtemplate'].objects.get(name="Пользовательское письмо").delete()
		orm['newsletter.newslettersettings'].objects.all()[0].delete()

	models = {
		'newsletter.job': {
			'Meta': {'object_name': 'Job'},
			'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'mail': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mails'", 'to': "orm['newsletter.Mail']"}),
			'recievers': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '125'}),
			'send_date': ('django.db.models.fields.DateField', [], {}),
			'state': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '1', 'decimal_places': '0'})
		},
		'newsletter.mail': {
			'Meta': {'object_name': 'Mail'},
			'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'subject': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
			'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'templates'", 'to': "orm['newsletter.MailTemplate']"}),
			'text': ('ckeditor.fields.RichTextField', [], {})
		},
		'newsletter.mailtemplate': {
			'Meta': {'object_name': 'MailTemplate'},
			'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
			'template': ('django.db.models.fields.TextField', [], {})
		},
		'newsletter.newslettersettings': {
			'Meta': {'object_name': 'NewsletterSettings'},
			'day': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
			'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'newsletter_type': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '125'})
		}
	}

	complete_apps = ['newsletter']
	symmetrical = True
