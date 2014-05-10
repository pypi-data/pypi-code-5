# coding=utf-8

from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    complete_apps = ['livesettings']
    models = {}

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass
