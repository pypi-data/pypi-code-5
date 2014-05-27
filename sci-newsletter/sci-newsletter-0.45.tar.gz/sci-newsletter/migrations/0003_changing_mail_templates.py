# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        template_text = orm['newsletter.mailtemplate'].objects.get(name="Ежемесячная рассылка")
        template_text.template="""
<b>Доброго времени суток!</b>
<br>
<i>На нашем сайте произошли следующие изменения:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта "{{res_name}}"</i>
"""
        template_text.save()

        template_text = orm['newsletter.mailtemplate'].objects.get(name="Пользовательское письмо")
        template_text.template="""
<b>Доброго времени суток!</b>
<br>
<i>У нас есть для вас следующая информация:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта "{{res_name}}"</i>
"""
        template_text.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        template_text = orm['newsletter.mailtemplate'].objects.get(name="Ежемесячная рассылка")
        template_text.template="""
<b>Доброго времени суток!</b>
<br>
<i>На нашем сайте произошли следующие изменения:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта SciBib</i>
"""
        template_text.save()

        template_text = orm['newsletter.mailtemplate'].objects.get(name="Пользовательское письмо")
        template_text.template="""
<b>Доброго времени суток!</b>
<br>
<i>У нас есть для вас следующая информация:</i>
<br>
{{text}}
<br>
<i>С уважением, администрация сайта SciBib</i>
"""
        template_text.save()

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
