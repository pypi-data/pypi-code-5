# Copyright 2010-2014 Canonical Ltd.
import functools
import uuid
from time import sleep
import logging

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from StringIO import StringIO

from keystoneclient.exceptions import AuthorizationFailure
from swiftclient import Connection, ClientException


def swift_retry_auth(func):
    @functools.wraps(func)
    def with_auth_retry(self, *args, **kwargs):
        tries = 3
        tried = 0

        while True:
            try:
                logging.debug("Attempting authorised request to Swift")
                result = func(self, *args, **kwargs)
                logging.debug("Authorised request successful")
                return result
            except AuthorizationFailure, e:
                tried = tried + 1
                logging.debug("Received Authorization failure %s (%d)" %
                    (str(e), tried))
                logging.debug("Parameters: %s" % args)
                if tried == tries:
                    logging.debug("Too many failures - raising an error.")
                    raise
                sleep(5)
                logging.debug("Slept for 5 seconds post Authorization failure")

    with_auth_retry.retries_auth = True
    return with_auth_retry


def swift_retry_container_404(func):
    @functools.wraps(func)
    def with_404_create(self, *args, **kwargs):
        tries = 1
        tried = 0
        while True:
            try:
                return func(self, *args, **kwargs)
            except ClientException, e:
                if not e.http_status == 404 or tried==tries:
                    raise
                tried = tried + 1
                self._get_connection().put_container(self.container_name)

    with_404_create.retries_auth = True
    return with_404_create


class SwiftStorage(Storage):
    """
    Storage class for openstack's swift.
    """
    def __init__(self, conn=None):
        self.conn = conn
        self.container_name = settings.SWIFT_CONTAINER_NAME

    @swift_retry_auth
    def read(self, name):
        """
        Reads a file from swift. Not part of the Django storage implementation,
        but makes sense for backend interactions to go on the storage class.
        """
        conn = self._get_connection()
        return conn.get_object(
            self.container_name, name)[1]

    @swift_retry_auth
    def size(self, name):
        """
        Returns the size of the named file.
        Part of the Django storage class implementation.
        """
        conn = self._get_connection()
        object_info = conn.head_object(
            self.container_name, name)
        if 'content-length' in object_info:
            return object_info['content-length']
        return 0

    @swift_retry_auth
    def url(self, name):
        """
        Returns an absolute URL to the stored content.
        Part of the Django storage class implementation.
        """
        return settings.MEDIA_URL + name

    @swift_retry_auth
    def delete(self, name):
        """
        Deletes the named file.
        Part of the Django storage class implementation.
        """
        conn = self._get_connection()
        return conn.delete_object(self.container_name, name)

    @swift_retry_auth
    def exists(self, name):
        """
        Returns boolean indicating if named file exists.
        Part of the Django storage class implementation.
        """
        conn = self._get_connection()
        try:
            conn.head_object(self.container_name, name)
        except ClientException:
            return False
        return True

    def get_available_name(self, name):
        """
        Generates a unique filename using uuid.uuid4 and the name
        passed in.
        Part of the Django storage class implementation.
        """
        return '%s-%s' % (uuid.uuid4(), name)

    @swift_retry_auth
    def put_object(self, name, content):
        """
        Puts an object into swift storage.
        Expects a file type object as content.
        """
        conn = self._get_connection()
        conn.put_object(self.container_name, name, content)

    def _get_connection(self):
        """
        Returns a swiftclient connection object using the credentials
        from settings.
        """
        if self.conn:
            return self.conn

        self.conn = Connection(
            settings.OS_AUTH_URL,
            settings.OS_USERNAME,
            settings.OS_PASSWORD,
            auth_version='2.0',
            os_options={
                'region_name': settings.OS_REGION_NAME,
                'tenant_id': None,
                'auth_token': None,
                'endpoint_type': None,
                'tenant_name': settings.OS_TENANT_NAME,
                'service_type': None,
                'object_storage_url': None},
            snet=False)
        return self.conn

    def _open(self, name, mode):
        """
        Returns a SwiftFile instance.
        Part of the Django storage class implementation.
        """
        return SwiftFile(name, self, mode)

    @swift_retry_container_404
    def _save(self, name, content):
        """
        Puts the file into swift, calling the put_object method.
        Part of the Django storage class implementation.
        """
        self.put_object(name, content)
        return name

class SwiftStaticStorage(SwiftStorage):
    """
    Static storage class for openstack's swift.
    """
    def __init__(self, conn=None):
        self.conn = conn
        self.container_name = settings.SWIFT_STATICCONTAINER_NAME
    
    @swift_retry_auth
    def exists(self, name):
        """
        Returns boolean indicating if named file exists.
        Part of the Django storage class implementation.
        """
        conn = self._get_connection()
        if hasattr(settings, 'SWIFT_STATICFILE_PREFIX') and settings.SWIFT_STATICFILE_PREFIX:
            name = settings.SWIFT_STATICFILE_PREFIX + name
        
        return super(SwiftStaticStorage, self).exists(name)

    @swift_retry_auth
    def url(self, name):
        """
        Returns an absolute URL to the stored content.
        Part of the Django storage class implementation.
        """
        if hasattr(settings, 'SWIFT_STATICFILE_PREFIX') and settings.SWIFT_STATICFILE_PREFIX is not None:
            return settings.STATIC_URL + settings.SWIFT_STATICFILE_PREFIX + name
        else:
            return settings.STATIC_URL + name

    def get_available_name(self, name):
        """
        Status files always use the same path as the name
        Part of the Django storage class implementation.
        """
        if hasattr(settings, 'SWIFT_STATICFILE_PREFIX') and settings.SWIFT_STATICFILE_PREFIX is not None:
            return settings.SWIFT_STATICFILE_PREFIX + name
        else:
            return name

    @swift_retry_auth
    def delete(self, name):
        """
        Deletes the named file.
        Part of the Django storage class implementation.
        """
        if hasattr(settings, 'SWIFT_STATICFILE_PREFIX') and settings.SWIFT_STATICFILE_PREFIX is not None:
            name = settings.SWIFT_STATICFILE_PREFIX + name
        return super(SwiftStaticStorage, self).delete(name)


class SwiftFile(File):
    """
    A file in openstack's swift.
    """
    def __init__(self, name, storage, mode):
        self.name = name
        self._storage = storage
        self._mode = mode
        self._dirty = False
        self._read_from_storage = False
        self.file = StringIO()

    @property
    def size(self):
        """
        Returns the size of the file.
        """
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self.name)
        return self._size

    def read(self, num_bytes=None):
        """
        Reads the file content from storage.
        """
        # if we haven't yet read the file from storage, do so
        if not self._read_from_storage:
            self.file = StringIO(self._storage.read(self.name))
            self._read_from_storage = True
        return self.file.read(num_bytes)

    def write(self, content):
        """
        Writes the file content to internal file if the file has been
        opened for write.
        """
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._dirty = True

    def close(self):
        """
        Closes the file. Sends the content to storage if the file has
        been written to.
        """
        if self._dirty:
            self._storage.put_object(self.name, self.file)
        self.file.close()
