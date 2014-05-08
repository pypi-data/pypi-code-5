# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IntellectMoney'
        db.create_table('intellectmoney_intellectmoney', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('orderId', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('intellectmoney', ['IntellectMoney'])


    def backwards(self, orm):
        # Deleting model 'IntellectMoney'
        db.delete_table('intellectmoney_intellectmoney')


    models = {
        'intellectmoney.intellectmoney': {
            'Meta': {'ordering': "['-created']", 'object_name': 'IntellectMoney'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orderId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['intellectmoney']