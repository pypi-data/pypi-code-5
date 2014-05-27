# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Order'
        db.create_table('django_postnl_checkout_order', (
            ('order_token', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('order_ext_ref', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('order_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('customer_ext_ref', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('prepare_order_request', self.gf('jsonfield.fields.JSONField')(default={})),
            ('prepare_order_response', self.gf('jsonfield.fields.JSONField')(default={})),
            ('read_order_response', self.gf('jsonfield.fields.JSONField')(default={})),
            ('update_order_request', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('django_postnl_checkout', ['Order'])


    def backwards(self, orm):
        # Deleting model 'Order'
        db.delete_table('django_postnl_checkout_order')


    models = {
        'django_postnl_checkout.order': {
            'Meta': {'object_name': 'Order'},
            'customer_ext_ref': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'order_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'order_ext_ref': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'order_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'prepare_order_request': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'prepare_order_response': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'read_order_response': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'update_order_request': ('jsonfield.fields.JSONField', [], {'default': '{}'})
        }
    }

    complete_apps = ['django_postnl_checkout']