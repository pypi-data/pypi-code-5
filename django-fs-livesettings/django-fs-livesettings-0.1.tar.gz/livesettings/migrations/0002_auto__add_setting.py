# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table(u'livesettings_setting', (
            ('key', self.gf('livesettings.fields.KeyField')(max_length=254, primary_key=True)),
            ('tpe', self.gf('django.db.models.fields.CharField')(max_length=254, null=True, blank=True)),
            ('value', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=254, null=True, blank=True)),
        ))
        db.send_create_signal(u'livesettings', ['Setting'])


    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table(u'livesettings_setting')


    models = {
        u'livesettings.setting': {
            'Meta': {'object_name': 'Setting'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'key': ('livesettings.fields.KeyField', [], {'max_length': '254', 'primary_key': 'True'}),
            'tpe': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'value': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['livesettings']