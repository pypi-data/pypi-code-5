# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'IntellectMoney.payment_id'
        db.add_column('intellectmoney_intellectmoney', 'payment_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'IntellectMoney.payment_id'
        db.delete_column('intellectmoney_intellectmoney', 'payment_id')


    models = {
        'intellectmoney.intellectmoney': {
            'Meta': {'ordering': "['-created']", 'object_name': 'IntellectMoney'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orderId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['intellectmoney']