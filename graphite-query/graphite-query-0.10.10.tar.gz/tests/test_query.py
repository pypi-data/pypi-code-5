import os
import shutil

from __setup import TestCase

import time
import whisper
from graphite import settings
from graphite import query

class QueryTest(TestCase):
    _test_data = [0.5, 0.4, 0.6]

    def setUp(self):
        super(QueryTest, self).setUp()
        settings.CREATE_DIRECTORIES = False
        if not os.path.exists(settings.WHISPER_DIR):
            os.makedirs(settings.WHISPER_DIR)
        if not settings.STANDARD_DIRS:
            raise Exception("settings.STANDARD_DIRS shouldn't be empty")
        self.populate_data()

    def populate_data(self):
        self.db = os.path.join(settings.WHISPER_DIR, 'test.wsp')
        whisper.create(self.db, [(1, 60)])
        ts = int(time.time())
        for i, value in enumerate(reversed(self._test_data)):
            whisper.update(self.db, value, ts - i)
        self.ts = ts

    def test_query(self):
        data = query.query({'target': 'test'})
        end = data[0]#[-4:]
        match = False
        # We iterate through all values and check
        # _test_data against 3 consecutive values
        # because sometimes whisper adds None
        # value(s) to the end (depending on time)
        for i, value in enumerate(end):
            if value == self._test_data[0]:
                self.assertEqual(end[i:i+3], self._test_data)
                match = True
                break
        self.assertTrue(match)

    def test_params_type(self):
        self.assertRaises(TypeError, query.query, "target:localhost")

    def test_all_None(self):
        whisper.create(os.path.join(settings.WHISPER_DIR, 'test_all_None.wsp'), [(1, 60)])
        data = query.query({'target': 'test_all_None'})
        self.assertNotEqual(data, [])

    def test_change_STANDARD_DIRS(self):
        " A test against a bug that was found in StandardFinder.directories "
        # This sets up whatever was the default storage directory layout
        from graphite import settings
        # We remove the default storage dir
        shutil.rmtree(settings.STORAGE_DIR, ignore_errors=True)
        # Now change the storage directory
        STORAGE_DIR_new = settings.STORAGE_DIR + '_new'
        # Remove if exists
        shutil.rmtree(STORAGE_DIR_new, ignore_errors=True)
        settings.setup_storage_variables(STORAGE_DIR_new, create_directories=True)
        self.populate_data()
        data = query.query({'target': 'test'})
        self.assertTrue(data[0])
