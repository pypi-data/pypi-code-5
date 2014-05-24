# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'App'
        db.create_table('api_app', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_apps', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('callback_url', self.gf('django.db.models.fields.URLField')(max_length=255, null=True, blank=True)),
            ('deployment', self.gf('django.db.models.fields.CharField')(default='', max_length=1)),
            ('http_login', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('http_signup', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('bambu_api', ['App'])

        # Adding model 'Nonce'
        db.create_table('api_nonce', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token_key', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('consumer_key', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('bambu_api', ['Nonce'])

        # Adding model 'Token'
        db.create_table('api_token', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('verifier', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('token_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.PositiveIntegerField')(default=1400931659L)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tokens', null=True, to=orm['auth.User'])),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tokens', to=orm['bambu_api.App'])),
            ('callback', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('callback_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('bambu_api', ['Token'])

        # Adding model 'RequestBatch'
        db.create_table('api_requestbatch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requests', to=orm['bambu_api.App'])),
            ('timestamp', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('bambu_api', ['RequestBatch'])

        # Adding unique constraint on 'RequestBatch', fields ['app', 'timestamp']
        db.create_unique('api_requestbatch', ['app_id', 'timestamp'])


    def backwards(self, orm):
        # Removing unique constraint on 'RequestBatch', fields ['app', 'timestamp']
        db.delete_unique('api_requestbatch', ['app_id', 'timestamp'])

        # Deleting model 'App'
        db.delete_table('api_app')

        # Deleting model 'Nonce'
        db.delete_table('api_nonce')

        # Deleting model 'Token'
        db.delete_table('api_token')

        # Deleting model 'RequestBatch'
        db.delete_table('api_requestbatch')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bambu_api.app': {
            'Meta': {'ordering': "('name',)", 'object_name': 'App', 'db_table': "'api_app'"},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_apps'", 'to': u"orm['auth.User']"}),
            'callback_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'deployment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'http_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'http_signup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'bambu_api.nonce': {
            'Meta': {'object_name': 'Nonce', 'db_table': "'api_nonce'"},
            'consumer_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'token_key': ('django.db.models.fields.CharField', [], {'max_length': '18'})
        },
        'bambu_api.requestbatch': {
            'Meta': {'unique_together': "(('app', 'timestamp'),)", 'object_name': 'RequestBatch', 'db_table': "'api_requestbatch'"},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requests'", 'to': "orm['bambu_api.App']"}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'bambu_api.token': {
            'Meta': {'object_name': 'Token', 'db_table': "'api_token'"},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tokens'", 'to': "orm['bambu_api.App']"}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'callback': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'callback_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1400931659L'}),
            'token_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tokens'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'verifier': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bambu_api']