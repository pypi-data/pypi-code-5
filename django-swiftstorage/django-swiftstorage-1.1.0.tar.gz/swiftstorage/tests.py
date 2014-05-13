# This file is part of django-swiftstorage.
# Copyright 2014 Canonical Ltd.

# django-swiftstorage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uuid
import unittest
import os
from StringIO import StringIO
import logging

import mocker

from django.conf import settings
settings.configure(
    DEFAULT_FILE_STORAGE="swiftstorage.storage.SwiftStorage",
    OS_USERNAME="testing",
    OS_PASSWORD="password",
    OS_AUTH_URL="https://keystone.example.com:443/v2.0/",
    OS_REGION_NAME="testregion",
    OS_TENANT_NAME="testtenant",
    SWIFT_CONTAINER_NAME="testcontainer",
)
    
from django.test import SimpleTestCase
from django.test.utils import override_settings

from keystoneclient.exceptions import AuthorizationFailure
from swiftclient import Connection, ClientException

from swiftstorage.storage import swift_retry_auth, SwiftFile, SwiftStorage, SwiftStaticStorage


class LoggingCaptureMixin(object):

    def setUp(self):
        super(LoggingCaptureMixin, self).setUp()
        self._loggers = []

    def capture_logging(self, logger_name="", log_level=logging.INFO,
                        format="", propagate=False):
        """
        Call this with an optional logger_name and this will log the named
        logger into a log_file (StringIO) that is returned.

        Defaults to a non-propagating handler, which is useful if you have a
        test environment that sets up its own handlers...
        """
        log_file = StringIO()
        log_handler = logging.StreamHandler(log_file)
        log_handler.propagate = propagate
        logger = logging.getLogger(logger_name)
        logger.addHandler(log_handler)

        if format:
            log_handler.setFormatter(logging.Formatter(format))

        old_logger_level = logger.level
        if log_level:
            logger.setLevel(log_level)
        self._loggers.append((logger, log_handler, old_logger_level))
        return log_file

    def tearDown(self):
        for logger, handler, old_level in reversed(self._loggers):
            logger.removeHandler(handler)
            logger.setLevel(old_level)
        super(LoggingCaptureMixin, self).tearDown()


@unittest.skipUnless(
        os.environ.get('OS_REGION_NAME', False) and
        os.environ.get('OS_PASSWORD', False) and
        os.environ.get('OS_AUTH_URL', False) and
        os.environ.get('OS_USERNAME', False) and
        os.environ.get('OS_TENANT_NAME', False),
        'OpenStack environment vars were not set.')
@override_settings(SWIFT_CONTAINER_NAME=str(uuid.uuid4()))
class SwiftIntegrationTestCase(SimpleTestCase):
    def setUp(self):
        super(SwiftIntegrationTestCase, self).setUp()
        self.conn = Connection(
            os.environ.get('OS_AUTH_URL'),
            os.environ.get('OS_USERNAME'),
            os.environ.get('OS_PASSWORD'),
            auth_version='2.0',
            os_options={
                'region_name': os.environ.get('OS_REGION_NAME'),
                'tenant_id': None,
                'auth_token': None,
                'endpoint_type': None,
                'tenant_name': os.environ.get('OS_TENANT_NAME'),
                'service_type': None,
                'object_storage_url': None},
            snet=False)
        self.conn.put_container(settings.SWIFT_CONTAINER_NAME)

    def tearDown(self):
        super(SwiftIntegrationTestCase, self).tearDown()
        to_delete = self.conn.get_container(settings.SWIFT_CONTAINER_NAME)[1]
        for obj in to_delete:
            self.conn.delete_object(settings.SWIFT_CONTAINER_NAME, obj['name'])
        self.conn.delete_container(settings.SWIFT_CONTAINER_NAME)

    def test_save_and_read_back_file(self):
        """
        Test the storage will save a file using swift.
        """
        storage = SwiftStorage(conn=self.conn)
        content = StringIO('my content')
        remote_filename = storage.save('my filename', content)
        swiftfile_read = SwiftFile(remote_filename, storage, 'r')
        self.assertEqual('my content', swiftfile_read.read())

    def test_save_and_check_exists(self):
        """
        Once a file has been saved, exists should return True.
        """
        storage = SwiftStorage(conn=self.conn)
        content = StringIO('my content')
        remote_filename = storage.save('my filename', content)
        self.assertTrue(storage.exists(remote_filename))

    def test_save_then_delete_then_exists(self):
        """
        Once a file has been saved, then deleted, exists should
        return False.
        """
        storage = SwiftStorage(conn=self.conn)
        content = StringIO('my content')
        remote_filename = storage.save('my filename', content)
        storage.delete(remote_filename)
        self.assertFalse(storage.exists(remote_filename))


@override_settings(
    OS_REGION_NAME='lcy01',
    OS_PASSWORD='ABCDEFG12345',
    OS_AUTH_URL='https://keystone.canonistack.canonical.com:443/v2.0/',
    OS_USERNAME='user',
    OS_TENANT_NAME='user_project',
    SWIFT_CONTAINER_NAME='user_container')
class SwiftStorageTestCase(LoggingCaptureMixin, mocker.MockerTestCase, SimpleTestCase):
    """
    Test for SwiftStorage and the interactions with swiftclient.
    """
    def setUp(self):
        super(SwiftStorageTestCase, self).setUp()
        self.mock_conn_class = self.mocker.replace(Connection)

    def _setup_connection_expectation(self):
        """
        Prepares mocker to expect a connection instantiation.
        """
        self.mock_conn_class(
            'https://keystone.canonistack.canonical.com:443/v2.0/',
            'user',
            'ABCDEFG12345',
            auth_version='2.0',
            os_options={
                'region_name': 'lcy01',
                'tenant_id': None,
                'auth_token': None,
                'endpoint_type': None,
                'tenant_name': 'user_project',
                'service_type': None,
                'object_storage_url': None},
            snet=False)
        mock_conn = self.mocker.mock()
        self.mocker.result(mock_conn)
        return mock_conn

    def test_get_available_name(self):
        """
        get_available_name will return a uuid prepended to the
        original name.
        """
        mock_uuid = self.mocker.replace(uuid)
        mock_uuid.uuid4()
        self.mocker.result('unique-id')
        self.mocker.replay()
        storage = SwiftStorage()
        self.assertEqual('unique-id-name', storage.get_available_name('name'))

    def test_open(self):
        """
        open will return a SwiftFile with the storage and mode passed in.
        """
        filename = 'somefile'
        mode = 'r'
        storage = SwiftStorage()
        mock_swiftfile = self.mocker.replace(SwiftFile)
        mock_swiftfile(filename, storage, mode)
        self.mocker.result(True)
        self.mocker.replay()
        self.assertTrue(storage.open(filename, mode))

    def test_save(self):
        """
        When passed a filename and a file object, they will be passed
        to the swiftclient's Connection.put_object
        """
        storage = SwiftStorage()
        file_obj = StringIO('some content')
        mock_conn = self._setup_connection_expectation()
        mock_uuid = self.mocker.replace(uuid)
        mock_uuid.uuid4()
        self.mocker.result('unique-id')
        mock_conn.put_object('user_container', 'unique-id-filename', file_obj)
        self.mocker.replay()
        storage.save('filename', file_obj)

    def test_save_with_nonexistent_container(self):
        """
        When passed a filename and a file object, they will be passed
        to the swiftclient's Connection.put_object
        """
        storage = SwiftStorage()
        file_obj = StringIO('some content')
        with self.mocker.order():
            mock_uuid = self.mocker.replace(uuid)
            mock_uuid.uuid4()
            self.mocker.result('unique-id')
            mock_conn = self._setup_connection_expectation()
            mock_conn.put_object(
                settings.SWIFT_CONTAINER_NAME, 'unique-id-filename',
                file_obj)
            self.mocker.throw(
                ClientException('Object PUT failed', http_status=404,
                                http_reason='Container not found',
                                http_response_content=''))
            mock_conn.put_container(settings.SWIFT_CONTAINER_NAME)
            mock_conn.put_object(
                settings.SWIFT_CONTAINER_NAME, 'unique-id-filename', file_obj)

        self.mocker.replay()

        storage.save('filename', file_obj)

    def test_size(self):
        """
        Calls head_object on the swiftclient connection and returns the file
        size.
        """
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_container', 'filename')
        self.mocker.result({'content-length': 42})
        self.mocker.replay()
        self.assertEqual(42, storage.size('filename'))

    def test_size_with_no_content_length(self):
        """
        Swift does not give a content-length for zero length files.
        We should return 0 if there is no content-length.
        """
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_container', 'filename')
        self.mocker.result({})
        self.mocker.replay()
        self.assertEqual(0, storage.size('filename'))

    def test_delete(self):
        """
        Calls delete_object on the swiftclient connection with the filename
        """
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.delete_object('user_container', 'filename')
        self.mocker.replay()
        self.assertEqual(None, storage.delete('filename'))

    def test_exists_existing(self):
        """
        exists should return True if Connection.head_object is successful.
        """
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_container', 'filename')
        self.mocker.result(
            {'x-account-object-count': '1',
            'x-timestamp': '1352817188.77356',
            'date': 'Wed, 14 Nov 2012 19:47:23 GMT',
            'x-account-bytes-used': '20', 'x-account-container-count': '1',
            'accept-ranges': 'bytes'})
        self.mocker.replay()
        self.assertTrue(storage.exists('filename'))

    def test_exists_nonexisting(self):
        """
        exists should return False if Connection.head_object raises an
        exception.
        """
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_container', 'filename')
        self.mocker.throw(ClientException('Object HEAD failed'))
        self.mocker.replay()
        self.assertFalse(storage.exists('filename'))

    def test_read(self):
        """
        read should read a file from the swiftclient connection.
        """
        filename = 'fname'
        content = '1234'
        storage = SwiftStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.get_object('user_container', filename)
        self.mocker.result(
            ({
                'content-length': '4',
                'accept-ranges': 'bytes',
                'last-modified': 'Thu, 15 Nov 2012 04:42:49 GMT',
                'etag': '81dc9bdb52d04dc20036dbd8313ed055',
                'x-timestamp': '1352954569.74936',
                'date': 'Thu, 15 Nov 2012 04:51:33 GMT',
                'content-type': 'application/octet-stream'},
                content))
        self.mocker.replay()
        self.assertEqual(content, storage.read(filename))

    def test_decorator_retries_on_auth_fail(self):
        """
        Due to swift not authenticating correctly all the time, the
        retry_auth decorator should retry authentication if it catches
        an authentication fail.

        The code should retry three times, and raise the exception if it
        is thrown again.
        """
        log_file = self.capture_logging(log_level=logging.DEBUG)
        mock_sleep = self.mocker.replace('time.sleep')
        mock_sleep(5)
        self.mocker.result(None)
        mock_sleep(5)
        self.mocker.result(None)
        self.mocker.replay()

        def method_that_interacts_with_swift(self, argument):
            if argument == 'fail':
                raise AuthorizationFailure('Auth failed')

        decorated = swift_retry_auth(method_that_interacts_with_swift)
        with self.assertRaises(AuthorizationFailure) as context:
            decorated(None, 'fail')
            self.assertEqual('Auth failed', str(context.exception))

        self.assertEqual(
            "Attempting authorised request to Swift\n"
            "Received Authorization failure Auth failed (1)\n"
            "Parameters: fail\n"
            "Slept for 5 seconds post Authorization failure\n"
            "Attempting authorised request to Swift\n"
            "Received Authorization failure Auth failed (2)\n"
            "Parameters: fail\n"
            "Slept for 5 seconds post Authorization failure\n"
            "Attempting authorised request to Swift\n"
            "Received Authorization failure Auth failed (3)\n"
            "Parameters: fail\n"
            "Too many failures - raising an error.\n",
            log_file.getvalue())

    def test_swiftstorage_methods_are_decorated(self):
        """
        Test that each method on SwiftStorage is decorated with the
        swift_retry_auth decorator.
        """
        self.mocker.replay()
        storage = SwiftStorage()
        self.assertTrue(storage.read.retries_auth)
        self.assertTrue(storage.size.retries_auth)
        self.assertTrue(storage.delete.retries_auth)
        self.assertTrue(storage.exists.retries_auth)
        self.assertTrue(storage.put_object.retries_auth)

    def test_instance_container_name(self):
        """
        Test that the container name used by a storage instance will
        not change after it was created, even when the source of it's
        original value changes
        """
        self.mocker.replay()
        storage = SwiftStorage()
        self.assertEqual('user_container', storage.container_name)

        with override_settings(SWIFT_CONTAINER_NAME='test_container'):
            self.assertEqual('user_container', storage.container_name)

            new_storage = SwiftStorage()
            self.assertEqual('test_container', new_storage.container_name)


@override_settings(
    OS_REGION_NAME='lcy01',
    OS_PASSWORD='ABCDEFG12345',
    OS_AUTH_URL='https://keystone.canonistack.canonical.com:443/v2.0/',
    OS_USERNAME='user',
    OS_TENANT_NAME='user_project',
    DEFAULT_FILE_STORAGE="swiftstorage.storage.SwiftStaticStorage",
    STATIC_FILE_STORAGE="swiftstorage.storage.SwiftStaticStorage",
    SWIFT_STATICCONTAINER_NAME='user_staticcontainer',
    STATIC_URL='http://example.com/')
class SwiftStaticStorageTestCase(LoggingCaptureMixin, mocker.MockerTestCase, SimpleTestCase):
    """
    Test for SwiftStaticStorage and the interactions with swiftclient.
    """
    def setUp(self):
        super(SwiftStaticStorageTestCase, self).setUp()
        self.mock_conn_class = self.mocker.replace(Connection)

    def _setup_connection_expectation(self):
        """
        Prepares mocker to expect a connection instantiation.
        """
        self.mock_conn_class(
            'https://keystone.canonistack.canonical.com:443/v2.0/',
            'user',
            'ABCDEFG12345',
            auth_version='2.0',
            os_options={
                'region_name': 'lcy01',
                'tenant_id': None,
                'auth_token': None,
                'endpoint_type': None,
                'tenant_name': 'user_project',
                'service_type': None,
                'object_storage_url': None},
            snet=False)
        mock_conn = self.mocker.mock()
        self.mocker.result(mock_conn)
        return mock_conn

    def test_static_container_name(self):
        """
        Test that SwiftStaticStorage uses the SWIFT_STATICCONTAINER_NAME
        instead of SWIFT_CONTAINER_NAME
        """
        self.mocker.replay()
        storage = SwiftStaticStorage()
        self.assertEqual('user_staticcontainer', storage.container_name)

        with override_settings(SWIFT_STATICCONTAINER_NAME='test_staticcontainer'):
            self.assertEqual('user_staticcontainer', storage.container_name)

            new_storage = SwiftStaticStorage()
            self.assertEqual('test_staticcontainer', new_storage.container_name)

    def test_get_available_name(self):
        """
        get_available_name will return an unaltered name when
        settings.SWIFT_STATICFILE_PREFIX is not set
        """
        self.mocker.replay()
        storage = SwiftStaticStorage()
        self.assertEqual('original-name', storage.get_available_name('original-name'))

    def test_get_available_name_staticfile_prefix(self):
        """
        get_available_name will return the original name prefixed with
        settings.SWIFT_STATICFILE_PREFIX when it is set
        """
        self.mocker.replay()
        with override_settings(SWIFT_STATICFILE_PREFIX='test-prefix/'):
            storage = SwiftStaticStorage()
            self.assertEqual('test-prefix/original-name', storage.get_available_name('original-name'))

    def test_url(self):
        """
        get_available_name will return an unaltered name when
        settings.SWIFT_STATICFILE_PREFIX is not set
        """
        self.mocker.replay()
        storage = SwiftStaticStorage()
        self.assertEqual('http://example.com/original-name', storage.url('original-name'))


    def test_url_staticfile_prefix(self):
        """
        get_available_name will return an unaltered name when
        settings.SWIFT_STATICFILE_PREFIX is not set
        """
        self.mocker.replay()
        with override_settings(SWIFT_STATICFILE_PREFIX='test-prefix/'):
            storage = SwiftStaticStorage()
            self.assertEqual('http://example.com/test-prefix/original-name', storage.url('original-name'))

    def test_delete_existing(self):
        """
        Calls delete_object on the swiftclient connection with the filename
        """
        storage = SwiftStaticStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.delete_object('user_staticcontainer', 'filename')
        self.mocker.result(True)
        self.mocker.replay()
        self.assertEqual(True, storage.delete('filename'))

    def test_delete_nonexisting(self):
        """
        Calls delete_object on the swiftclient connection with the filename
        """
        storage = SwiftStaticStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.delete_object('user_staticcontainer', 'filename')
        self.mocker.result(False)
        self.mocker.replay()
        self.assertEqual(False, storage.delete('filename'))

    def test_exists_existing(self):
        """
        exists should return True if Connection.head_object is successful.
        """
        storage = SwiftStaticStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_staticcontainer', 'filename')
        self.mocker.result(
            {'x-account-object-count': '1',
            'x-timestamp': '1352817188.77356',
            'date': 'Wed, 14 Nov 2012 19:47:23 GMT',
            'x-account-bytes-used': '20', 'x-account-container-count': '1',
            'accept-ranges': 'bytes'})
        self.mocker.replay()
        self.assertTrue(storage.exists('filename'))

    def test_exists_nonexisting(self):
        """
        exists should return False if Connection.head_object raises an
        exception.
        """
        storage = SwiftStaticStorage()
        mock_conn = self._setup_connection_expectation()
        mock_conn.head_object('user_staticcontainer', 'filename')
        self.mocker.throw(ClientException('Object HEAD failed'))
        self.mocker.replay()
        self.assertFalse(storage.exists('filename'))

class SwiftFileTestCase(mocker.MockerTestCase, SimpleTestCase):
    """
    Test for SwiftFile and the interactions between SwiftFile
    SwiftStorage.
    """
    def test_size(self):
        """
        Test that the file asks the storage for the file's size.
        """
        filename = 'myfile'
        filesize = 42
        mock_storage = self.mocker.mock()
        mock_storage.size(filename)
        self.mocker.result(filesize)
        self.mocker.replay()

        self.assertEqual(
            filesize,
            SwiftFile(filename, mock_storage, 'r').size)

    def test_size_cached(self):
        """
        Test that the storage is only queried the first time size is requested.
        """
        filename = 'myfile'
        filesize = 42
        mock_storage = self.mocker.mock()
        mock_storage.size(filename)
        self.mocker.result(filesize)
        self.mocker.replay()
        swiftfile = SwiftFile(filename, mock_storage, 'r')
        self.assertEqual(filesize, swiftfile.size)
        self.assertEqual(filesize, swiftfile.size)

    def test_write(self):
        """
        Test that the internal file has data written to it, but the storage
        is not accessed.
        """
        content = 'my content'
        mock_storage = self.mocker.mock()
        self.mocker.replay()
        swiftfile = SwiftFile('filename', mock_storage, 'w')
        swiftfile.write(content)
        self.assertEqual(content, swiftfile.file.read())

    def test_cant_write_to_file_not_opened_for_write(self):
        """
        If the file mode does not have 'w' in it, an AttributeError
        is raised.
        """
        mock_storage = self.mocker.mock()
        self.mocker.replay()
        swiftfile = SwiftFile('filename', mock_storage, 'r')
        with self.assertRaises(AttributeError) as context:
            swiftfile.write('content')
        self.assertEqual(
            'File was opened for read-only access.',
            str(context.exception))

    def test_close_file_that_hasnt_been_written_to_does_not_hit_storage(self):
        """
        Calling close on a file that has not been written to will not
        call any methods on the storage.
        """
        mock_storage = self.mocker.mock()
        self.mocker.replay()
        swiftfile = SwiftFile('filename', mock_storage, 'w')
        swiftfile.close()

    def test_close_file_with_written_data(self):
        """
        Closing the file will send the content to storage and call close
        on the internal file, if there has been data written.
        """
        filename = 'myfile'
        content = 'content'
        mock_storage = self.mocker.mock()
        mock_io = self.mocker.mock()
        # We have to use spec=None here because we can't patch the class because
        # it's a built-in.
        mock_file = self.mocker.replace(StringIO, spec=None)
        # new string io should be crated with the content
        mock_file(content)
        self.mocker.result(mock_io)
        # resulting io instance sent to put_object on the storage
        mock_storage.put_object(filename, mock_io)
        self.mocker.result(None)
        # io object closed
        mock_io.close()
        self.mocker.replay()

        swiftfile = SwiftFile(filename, mock_storage, 'w')
        swiftfile.write(content)
        swiftfile.close()

    def test_close_file_with_no_written_data(self):
        """
        Closing the file will call close on the internal file but not hit
        storage if write has not been called.
        """
        mock_storage = self.mocker.mock()
        self.mocker.replay()
        swiftfile = SwiftFile('filename', mock_storage, 'w')
        swiftfile.close()
        self.assertTrue(
            swiftfile.file.closed,
            'Internal file was not closed.')

    def test_read_from_storage(self):
        """
        Calling read will read the file from storage and return the file
        contents.
        """
        filename = 'myfile'
        content = 'content'
        mock_storage = self.mocker.mock()
        mock_storage.read(filename)
        self.mocker.result(content)
        self.mocker.replay()
        swiftfile = SwiftFile(filename, mock_storage, 'w')
        self.assertEqual(content, swiftfile.read())

    def test_multiple_reads(self):
        """
        Multiple reads will only hit the storage once.
        """
        filename = 'myfile'
        content = 'content'
        mock_storage = self.mocker.mock()
        mock_storage.read(filename)
        self.mocker.result(content)
        self.mocker.replay()
        swiftfile = SwiftFile(filename, mock_storage, 'w')
        self.assertEqual(content[:4], swiftfile.read(4))
        self.assertEqual(content[4:], swiftfile.read(4))
