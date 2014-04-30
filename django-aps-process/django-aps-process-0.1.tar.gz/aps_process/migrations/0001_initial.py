# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Buffer'
        db.create_table(u'aps_process_buffer', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rght', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lvl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='xchildren', null=True, to=orm['aps_process.Buffer'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='default', max_length=20, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='buffers', null=True, to=orm['aps_process.Location'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='buffers', to=orm['aps_process.Item'])),
            ('onhand', self.gf('django.db.models.fields.DecimalField')(default='0.0', null=True, max_digits=15, decimal_places=4, blank=True)),
            ('minimum', self.gf('django.db.models.fields.DecimalField')(default='0.0', null=True, max_digits=15, decimal_places=4, blank=True)),
            ('minimum_calendar', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='buffers', null=True, to=orm['aps_process.Calendar'])),
            ('producing', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='buffers', null=True, to=orm['aps_process.Operation'])),
            ('carrying_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('leadtime', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('fence', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('min_inventory', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('max_inventory', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('size_minimum', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('size_multiple', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('size_maximum', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Buffer'])

        # Adding model 'Calendar'
        db.create_table(u'aps_process_calendar', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('defaultvalue', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Calendar'])

        # Adding model 'CalendarBucket'
        db.create_table(u'aps_process_calendarbucket', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(related_name='buckets', to=orm['aps_process.Calendar'])),
            ('startdate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('enddate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2050, 12, 30, 0, 0), null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.DecimalField')(default='0.0', null=True, max_digits=15, decimal_places=4, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('monday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tuesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wednesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('thursday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('friday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('saturday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sunday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('starttime', self.gf('django.db.models.fields.TimeField')(default=datetime.time(0, 0), null=True, blank=True)),
            ('endtime', self.gf('django.db.models.fields.TimeField')(default=datetime.time(23, 59, 59), null=True, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['CalendarBucket'])

        # Adding model 'Flow'
        db.create_table(u'aps_process_flow', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flows', to=orm['aps_process.Operation'])),
            ('thebuffer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flows', to=orm['aps_process.Buffer'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default='1.0', max_digits=15, decimal_places=4)),
            ('type', self.gf('django.db.models.fields.CharField')(default='start', max_length=20)),
            ('effective_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('effective_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('alternate', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Flow'])

        # Adding unique constraint on 'Flow', fields ['operation', 'thebuffer']
        db.create_unique(u'aps_process_flow', ['operation_id', 'thebuffer_id'])

        # Adding model 'Item'
        db.create_table(u'aps_process_item', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rght', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lvl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='xchildren', null=True, to=orm['aps_process.Item'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='items', null=True, to=orm['aps_process.Operation'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Item'])

        # Adding model 'Location'
        db.create_table(u'aps_process_location', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rght', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lvl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='xchildren', null=True, to=orm['aps_process.Location'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('available', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='locations', null=True, to=orm['aps_process.Calendar'])),
        ))
        db.send_create_signal(u'aps_process', ['Location'])

        # Adding model 'Operation'
        db.create_table(u'aps_process_operation', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='fixed_time', max_length=20, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='operations', null=True, to=orm['aps_process.Location'])),
            ('setup', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('batchqty', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('batchtime', self.gf('django.db.models.fields.DecimalField')(default='1.0', null=True, max_digits=15, decimal_places=4, blank=True)),
            ('setdown', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Operation'])

        # Adding model 'Resource'
        db.create_table(u'aps_process_resource', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rght', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lvl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='xchildren', null=True, to=orm['aps_process.Resource'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('maximum', self.gf('django.db.models.fields.DecimalField')(default='1.0', null=True, max_digits=15, decimal_places=4, blank=True)),
            ('maximum_calendar', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resources', null=True, to=orm['aps_process.Calendar'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resources', null=True, to=orm['aps_process.Location'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('maxearly', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
            ('setupmatrix', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resources', null=True, to=orm['aps_process.SetupMatrix'])),
            ('setup', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['Resource'])

        # Adding model 'ResourceLoad'
        db.create_table(u'aps_process_resourceload', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='loads', to=orm['aps_process.Operation'])),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='loads', to=orm['aps_process.Resource'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default='1.0', max_digits=15, decimal_places=4)),
            ('effective_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('effective_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('alternate', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('setup', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('search', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['ResourceLoad'])

        # Adding unique constraint on 'ResourceLoad', fields ['operation', 'resource']
        db.create_unique(u'aps_process_resourceload', ['operation_id', 'resource_id'])

        # Adding model 'SetupMatrix'
        db.create_table(u'aps_process_setupmatrix', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
        ))
        db.send_create_signal(u'aps_process', ['SetupMatrix'])

        # Adding model 'SetupRule'
        db.create_table(u'aps_process_setuprule', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('setupmatrix', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rules', to=orm['aps_process.SetupMatrix'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('fromsetup', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('tosetup', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('duration', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=0, blank=True)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=4, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['SetupRule'])

        # Adding unique constraint on 'SetupRule', fields ['setupmatrix', 'priority']
        db.create_unique(u'aps_process_setuprule', ['setupmatrix_id', 'priority'])

        # Adding model 'SubOperation'
        db.create_table(u'aps_process_suboperation', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('lastmodified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suboperations', to=orm['aps_process.Operation'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('suboperation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='superoperations', to=orm['aps_process.Operation'])),
            ('effective_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('effective_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'aps_process', ['SubOperation'])


    def backwards(self, orm):
        # Removing unique constraint on 'SetupRule', fields ['setupmatrix', 'priority']
        db.delete_unique(u'aps_process_setuprule', ['setupmatrix_id', 'priority'])

        # Removing unique constraint on 'ResourceLoad', fields ['operation', 'resource']
        db.delete_unique(u'aps_process_resourceload', ['operation_id', 'resource_id'])

        # Removing unique constraint on 'Flow', fields ['operation', 'thebuffer']
        db.delete_unique(u'aps_process_flow', ['operation_id', 'thebuffer_id'])

        # Deleting model 'Buffer'
        db.delete_table(u'aps_process_buffer')

        # Deleting model 'Calendar'
        db.delete_table(u'aps_process_calendar')

        # Deleting model 'CalendarBucket'
        db.delete_table(u'aps_process_calendarbucket')

        # Deleting model 'Flow'
        db.delete_table(u'aps_process_flow')

        # Deleting model 'Item'
        db.delete_table(u'aps_process_item')

        # Deleting model 'Location'
        db.delete_table(u'aps_process_location')

        # Deleting model 'Operation'
        db.delete_table(u'aps_process_operation')

        # Deleting model 'Resource'
        db.delete_table(u'aps_process_resource')

        # Deleting model 'ResourceLoad'
        db.delete_table(u'aps_process_resourceload')

        # Deleting model 'SetupMatrix'
        db.delete_table(u'aps_process_setupmatrix')

        # Deleting model 'SetupRule'
        db.delete_table(u'aps_process_setuprule')

        # Deleting model 'SubOperation'
        db.delete_table(u'aps_process_suboperation')


    models = {
        u'aps_process.buffer': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Buffer'},
            'carrying_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fence': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'buffers'", 'to': u"orm['aps_process.Item']"}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'leadtime': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'lft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'buffers'", 'null': 'True', 'to': u"orm['aps_process.Location']"}),
            'lvl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_inventory': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'min_inventory': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'minimum': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'minimum_calendar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'buffers'", 'null': 'True', 'to': u"orm['aps_process.Calendar']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'onhand': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'xchildren'", 'null': 'True', 'to': u"orm['aps_process.Buffer']"}),
            'producing': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'buffers'", 'null': 'True', 'to': u"orm['aps_process.Operation']"}),
            'rght': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'size_maximum': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'size_minimum': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'size_multiple': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.calendar': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Calendar'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'defaultvalue': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.calendarbucket': {
            'Meta': {'ordering': "('calendar', 'id')", 'object_name': 'CalendarBucket'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'buckets'", 'to': u"orm['aps_process.Calendar']"}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2050, 12, 30, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'endtime': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(23, 59, 59)', 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'starttime': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)', 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'aps_process.flow': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('operation', 'thebuffer'),)", 'object_name': 'Flow'},
            'alternate': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'effective_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effective_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flows'", 'to': u"orm['aps_process.Operation']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '15', 'decimal_places': '4'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'thebuffer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flows'", 'to': u"orm['aps_process.Buffer']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'start'", 'max_length': '20'})
        },
        u'aps_process.item': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Item'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'lft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lvl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': u"orm['aps_process.Operation']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'xchildren'", 'null': 'True', 'to': u"orm['aps_process.Item']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'rght': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.location': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Location'},
            'available': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': u"orm['aps_process.Calendar']"}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'lft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lvl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'xchildren'", 'null': 'True', 'to': u"orm['aps_process.Location']"}),
            'rght': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.operation': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Operation'},
            'batchqty': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'batchtime': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'operations'", 'null': 'True', 'to': u"orm['aps_process.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'setdown': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'setup': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'fixed_time'", 'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.resource': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Resource'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'lft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resources'", 'null': 'True', 'to': u"orm['aps_process.Location']"}),
            'lvl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maxearly': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'maximum': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'maximum_calendar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resources'", 'null': 'True', 'to': u"orm['aps_process.Calendar']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'xchildren'", 'null': 'True', 'to': u"orm['aps_process.Resource']"}),
            'rght': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'setup': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'setupmatrix': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resources'", 'null': 'True', 'to': u"orm['aps_process.SetupMatrix']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.resourceload': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('operation', 'resource'),)", 'object_name': 'ResourceLoad'},
            'alternate': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'effective_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effective_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'loads'", 'to': u"orm['aps_process.Operation']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '15', 'decimal_places': '4'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'loads'", 'to': u"orm['aps_process.Resource']"}),
            'search': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'setup': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.setupmatrix': {
            'Meta': {'ordering': "('name',)", 'object_name': 'SetupMatrix'},
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'aps_process.setuprule': {
            'Meta': {'ordering': "('setupmatrix__name', 'priority')", 'unique_together': "(('setupmatrix', 'priority'),)", 'object_name': 'SetupRule'},
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '4', 'blank': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '0', 'blank': 'True'}),
            'fromsetup': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'setupmatrix': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['aps_process.SetupMatrix']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tosetup': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        u'aps_process.suboperation': {
            'Meta': {'ordering': "('operation__name', 'priority')", 'object_name': 'SubOperation'},
            'effective_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effective_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suboperations'", 'to': u"orm['aps_process.Operation']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'suboperation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'superoperations'", 'to': u"orm['aps_process.Operation']"})
        }
    }

    complete_apps = ['aps_process']
