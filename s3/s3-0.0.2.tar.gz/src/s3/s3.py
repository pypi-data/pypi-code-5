#!/usr/bin/python
"""
This program moves local files to and from Amazon's Simple Storage System.

Capability:
  - Test if file exists in S3 bucket
  - Upload file to S3 bucket
  - Download file from S3 bucket
  - Delete file from S3 bucket
  - Copy S3 file to S3 file
  - Update metadata of S3 file
  
TODO:
  - Create S3 bucket. 
  - Delete S3 bucket.
  - Configure S3 bucket.

S3 files also have metadata in addition to their content.  
metadata is a python dict i.e. a set of key, value pairs.

IMPLEMENTATION NOTES:
The implementation is based on tinys3.  I've kept the connection and request 
objects but changed their API so it is not compatible with tinys3 at all.
I do use tinys3's auth module with a change to the signing logic.

Paul Wexler, Apr 17, 2014

Copyright (C) 2014, Prometheus Research, LLC
"""
from .auth import S3Auth
from .util import LenWrapperStream

import base64
import hashlib
import httplib
import logging
import math
import os
import requests
import time
import xmltodict

#httplib.HTTPConnection.debuglevel = 1

MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB

version = '0.0.2'

class S3Facts:
    amz_metadata_prefix = 'x-amz-meta-'
    maximum_file_size = 5 * TB
    maximum_part_number = 10 * 1000
    maximum_part_size = 5 * GB
    minimum_part_size = 5 * MB
    multipart_threshhold = 100 * MB
    
class S3Name:
    """An S3 file name consists of a bucket and a key.  This pair uniquely 
    identifies the file within S3.  
    
    The S3Connection class methods take a remote_name argument which can be 
    either a string which is the key, or an instance of the S3Name class.  
    When no bucket is given the default_bucket established when the connection 
    is instantiated is used.
    
    In other words, the S3Name class provides a means of using a bucket other 
    than the default_bucket.
    """
    def __init__(self, key, bucket=None):
        self.key = key
        self.bucket = bucket

class S3Part:
    """
    part_number - ranges from 1 to S3Facts.maximum_part_number
    etag - returned by S3 for successful upload_part
    """
    def __init__(self, part_number, etag):
        self.part_number = part_number
        self.etag = etag

    def __str__(self):
        return 'part_number: %s, etag: %s' % (self.part_number, self.etag)

class S3Request(object):
    """Base request object.
    Altered directly from the tinys3.S3Request implementation.
    """
    def __init__(self, conn):
        self.auth = conn.auth
        self.tls = conn.tls
        self.endpoint = conn.endpoint

    def _bucket_url(self, bucket, key):
        protocol = 'https' if self.tls else 'http'
        return "%s://%s/%s/%s" % (
                protocol, 
                self.endpoint, 
                bucket, 
                key.lstrip('/'))

    def _get_metadata(self, headers):
        return dict((k, headers[k]) for k in headers  
                if k.startswith(S3Facts.amz_metadata_prefix) )
        
    def _send_request(
            self, 
            method,
            url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=None,
            proxies=None,
            verify=None,
            stream=None,
            cert=None):
        logging.debug(['_send_request', method, url, headers, params])
        return requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                files=files,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                proxies=proxies,
                verify=verify,
                stream=stream,
                cert=cert,
                )

    def send(self):
        raise NotImplementedError()

class S3Response:
    """
    ok - boolean - the response was/not ok.
    error - the error when the response was not ok.
    response - the response object returned by the requests module.
    """
    def __init__(self, ok=True, error='', response=None, **kwargs):
        self.ok = ok 
        self.error = error
        self.response = response
        self.__dict__.update(kwargs)

def get_content_md5(s):
    """
    Returns the base64-encoded 128-bit MD5 digest of the string s.
    """
    m = hashlib.md5()
    m.update(s)
    return base64.b64encode(m.digest())

class CopyS3Request(S3Request): 
    """
    send() returns S3Response instance
    """
    def __init__(self, 
            conn, 
            src_bucket, src_key, 
            dst_bucket, dst_key, 
            headers={},
            ):

        super(CopyS3Request, self).__init__(conn)
        self.src_bucket = src_bucket
        self.src_key = src_key
        self.dst_bucket = dst_bucket
        self.dst_key = dst_key
        self.headers = headers
        
        self.metadata = self._get_metadata(headers)        
        self.url = self._bucket_url(self.dst_bucket, self.dst_key)

    def send(self):
        remote_src = '/%s/%s' % (self.src_bucket, self.src_key)
        metadata_directive = 'REPLACE' if self.metadata else 'COPY'
        headers = {
                'x-amz-copy-source': remote_src,
                'x-amz-metadata-directive': metadata_directive,
                }

        if self.headers:
            headers.update(self.headers)

        logging.debug(['COPY', self.url, headers])

        r = self._send_request(
                'PUT',
                self.url,
                auth=self.auth,
                headers=headers)

        ok = False
        if r.status_code == 200:
            result = xmltodict.parse(r.content)
            if 'CopyObjectResult' in result:
                if 'ETag' in result ['CopyObjectResult']:
                    ok = True
        else:
            result = r.reason 
        
        error = '' if ok else 'unable to COPY %s to %s: %i %s: %s' % (
                remote_src,
                self.url,
                r.status_code,
                result,
                r.text)
        return S3Response(ok=ok, error=error, response=r)

class DeleteS3Request(S3Request): 
    """
    send() returns S3Response instance
    """
    def __init__(self,  conn, bucket, key):
        super(DeleteS3Request, self).__init__(conn)
        self.bucket = bucket
        self.key = key
        self.url = self._bucket_url(self.bucket, self.key)

    def send(self):
        logging.debug(['DELETE', self.url])
        r = self._send_request(
                'DELETE',
                self.url,
                auth=self.auth)
        ok = r.status_code == 204
        error = r.reason if ok else 'unable to DELETE %s: %i %s: %s' % (
                self.url,
                r.status_code,
                r.reason,
                r.text)
        return S3Response(ok=ok, error=error, response=r)
        
class ExistsS3Request(S3Request): 
    """
    send() returns S3Response instance
    """
    def __init__(self,  conn, bucket, key):
        super(ExistsS3Request, self).__init__(conn)
        self.bucket = bucket
        self.key = key
        self.url = self._bucket_url(self.bucket, self.key)

    def send(self):
        logging.debug(['HEAD', self.url])
        r = self._send_request(
                'HEAD',
                self.url,
                auth=self.auth)
        if r.status_code == 200:
            ok = True
            error = ''
        elif r.status_code == 404:
            ok = True
            error = r.reason
        else:
            ok = False
            error = 'unable to HEAD %s: %i %s: %s' % (
                    self.url, 
                    r.status_code, 
                    r.reason,
                    r.text)
        metadata = self._get_metadata(r.headers)
        return S3Response(ok=ok, error=error, response=r, metadata=metadata)
        
class ReadS3Request(S3Request): 
    """
    send() returns S3Response instance which includes a metadata attribute
    containing the metadata of the bucket/key.
    """
    def __init__(self,  conn, bucket, key, local_file):
        super(ReadS3Request, self).__init__(conn)
        self.bucket = bucket
        self.key = key
        self.fp = local_file
        self.url = self._bucket_url(self.bucket, self.key)
        self.part_size = S3Facts.multipart_threshhold

    def send(self):
        logging.debug(['GET', self.url])
        r = self._send_request(
                'GET',
                self.url,
                auth=self.auth,
                stream=True)
        for x in r.iter_content(chunk_size=self.part_size):
            self.fp.write(x)
        ok = r.status_code == 200
        error = r.reason if ok else 'unable to GET %s: %i %s: %s' % (
                self.url,
                r.status_code,
                r.reason,
                r.text)
        metadata = self._get_metadata(r.headers)
        return S3Response(ok=ok, error=error, response=r, metadata=metadata)

class UpdateMetadataS3Request(CopyS3Request):
    def __init__(self,  conn, bucket, key, headers={}):
        super(UpdateMetadataS3Request, self).__init__(
                conn, 
                bucket, key, 
                bucket, key, 
                headers=headers,
                )

class WriteS3Request(S3Request):
    """
    send() returns S3Response instance
    """
    def __init__(self,  conn, local_file, bucket, key, headers={}):
        super(WriteS3Request, self).__init__(conn)

        self.conn = conn
        self.fp = local_file
        self.bucket = bucket
        self.key = key
        self.headers = headers

        self.data = LenWrapperStream(self.fp)        
        self.url = self._bucket_url(self.bucket, self.key)

    def send(self):
        nbytes = len(self.data)
        if nbytes < S3Facts.multipart_threshhold:
            return self._upload()
        else:
            assert nbytes <= S3Facts.maximum_file_size
            # compute the smallest part_size that will accomodate the file.
            part_size = max(
                    S3Facts.minimum_part_size, 
                    int(math.ceil(float(nbytes) / S3Facts.maximum_part_number))
                    )
            self._begin_multipart()
            try:
                while nbytes:
                    part_size = min(part_size, nbytes)
                    part = self.fp.read(part_size)
                    self._upload_part(part_size, part)
                    nbytes -= part_size
                return self._end_multipart()
            except Exception, e:
                upload = '%s %s/%s' % (self.upload_id, self.bucket, self.key)
                s3_response = S3Response()
                try:
                    s3_response = self._abort_multipart()
                    if s3_response.ok:
                        s3_response.ok = False
                        error = "Upload %s aborted after exception %s" % (
                                upload,
                                e)
                        s3_response.error = error
                        return s3_response
                    else:
                        pass
                except Exception, e2:
                    s3_response.ok = False
                    s3_response.error = e2

                error = ('%s - Unable to abort %s: %s, after exception %s') % (
                        "CRITICAL ERROR",
                        upload,
                        s3_response.error,
                        e)
                s3_response.error = error
                return s3_response

    def _abort_multipart(self):
        logging.debug(['_abort_multipart', self.url])
        params = { 'uploadId': self.upload_id, }
        r = self._send_request(
                'DELETE',
                self.url,
                params=params,
                auth=self.auth)
        s3_response = S3Response(response=r)
        if r.status_code == 204:
            s3_response.ok = True
        else:
            s3_response.ok = False
            s3_response.error = r.reason
        return s3_response
    
    def _begin_multipart(self):
        logging.debug(['_begin_multipart', self.url])
        params = 'uploads'
        r = self._send_request(
                'POST',
                self.url,
                headers=self.headers,
                params=params,
                auth=self.auth)
        r.raise_for_status()
        result = xmltodict.parse(r.content)
        self.upload_id = result['InitiateMultipartUploadResult']['UploadId']
        self.part_number = 0
        self.parts = []
        logging.debug(['upload_id', self.upload_id])
        
    def _end_multipart(self):
        logging.debug(['_end_multipart', self.url])
        data = '<CompleteMultipartUpload>\n'
        for part in self.parts:
            data += '  <Part>\n'
            data += '    <PartNumber>%s</PartNumber>\n' % part.part_number
            data += '    <ETag>%s</ETag>\n' % part.etag
            data += '  </Part>\n'
        data += "</CompleteMultipartUpload>"
        params = { 'uploadId': self.upload_id, }
        headers = { 'Content-Length': len(data) }
        r = self._send_request(
                'POST',
                self.url,
                headers=headers,
                params=params,
                data=data,
                auth=self.auth)
        logging.info('\n' + data)
        if r.status_code != 200:
            raise Exception, "Unable to CompleteMultipartUpload: %s %s: %s" % (
                r.status_code,
                r.reason,
                r.text)
        logging.info('Upload of %s %s.' % (self.url, r.reason))
        return S3Response(
                r.status_code == 200, 
                r.reason, 
                r)
    
    def _upload(self):
        logging.debug(['_upload', self.url])
        r = self._send_request(
                'PUT',
                self.url,
                data=self.data,
                auth=self.auth,
                headers=self.headers)
        if r.status_code == 200:
            ok = True
            error = ''
        else:
            ok = False
            error = 'unable to PUT %s: %i %s: %s' % (
                    self.url, 
                    r.status_code, 
                    r.reason,
                    r.text)
        return S3Response(
                ok=ok, 
                error=error, 
                response=r)
    
    def _upload_part(self, part_size, part):
        """ headers:
        Content-Length        
        Content-MD5
        """
        logging.debug(['_upload_part', part_size, part[:10]])
        headers = {}
        params = {}

        headers['Content-Length'] = part_size
        headers['Content-MD5'] = get_content_md5(part)

        self.part_number += 1
        assert self.part_number <= S3Facts.maximum_part_number
        
        params['partNumber'] = self.part_number
        params['uploadId'] = self.upload_id
        try:
            r = self._send_request(
                    'PUT',
                    self.url,
                    headers=headers,
                    params=params,
                    data=part,
                    auth=self.auth)
            logging.debug([
                    '_upload_part', 
                    r.status_code, 
                    r.reason, 
                    params['partNumber']])
        except Exception, e:
            raise Exception, "Unable to PUT.  Exception: %s" % e
        if r.status_code != 200:
            raise Exception, "Unable to PUT (upload part): %s %s: %s" % (
                    r.status_code, 
                    r.reason, 
                    r.text)

        s3_part = S3Part(self.part_number, r.headers['Etag'])
        self.parts.append(s3_part)
        logging.info('Uploaded part %s' % s3_part)

   
class S3Connection(object):
    """
    Altered directly from the tinys3.connection implementation.
    """
    
    def __init__(
            self, 
            access_key_id,
            secret_access_key,
            default_bucket=None, 
            endpoint="s3.amazonaws.com", 
            tls=True, 
            ):
        """
        Creates a new S3 connection

        Params:
        access_key_id   - AWS access key (username)
        secret_access_key - AWS secret access key (password)
        default_bucket  - Sets the default bucket.  Default is None
        tls             - do/not use secure connection.  Default is True.
        endpoint        - Sets the s3 endpoint.  Default is s3.amazonaws.com
        """
        self.auth = S3Auth(access_key_id, secret_access_key)
        self.default_bucket = default_bucket
        self.endpoint = endpoint
        self.tls = tls

    def copy(self, remote_src, remote_dst, headers={}): 
        src_bucket, src_key = self._get_bucket_and_key(remote_src)
        dst_bucket, dst_key = self._get_bucket_and_key(remote_dst)
        r = CopyS3Request(
                self, 
                src_bucket, src_key,
                dst_bucket, dst_key,
                headers=headers)
        s3_response = r.send()
        return s3_response

    def delete(self, remote_name): 
        bucket, key = self._get_bucket_and_key(remote_name)
        r = DeleteS3Request(self, bucket, key)
        s3_response = r.send()
        return s3_response

    def exists(self, remote_name): 
        bucket, key = self._get_bucket_and_key(remote_name)
        r = ExistsS3Request(self, bucket, key)
        s3_response = r.send()
        return s3_response

    def read(self, remote_name, local_file): 
        bucket, key = self._get_bucket_and_key(remote_name)
        r = ReadS3Request(self, bucket, key, local_file)
        s3_response = r.send()
        return s3_response

    def update_metadata(self, remote_name, headers): 
        bucket, key = self._get_bucket_and_key(remote_name)
        r = UpdateMetadataS3Request(self, bucket, key, headers)
        s3_response = r.send()
        return s3_response

    def write(self, local_file, remote_name, headers={}):
        bucket, key = self._get_bucket_and_key(remote_name)
        r = WriteS3Request(
                self, 
                local_file, 
                bucket, 
                key, 
                headers=headers)
        s3_response = r.send()
        return s3_response

    def _get_bucket(self, bucket):
        """
        Verifies that we have a bucket for a request
        Params:
        bucket -    The name of the bucket we're trying to use, None if we want 
                    to use the default bucket.
        Returns:    The bucket to use for the request
        Raises:
        ValueError if no bucket was provided AND no default bucket was defined.
        """
        b = bucket or self.default_bucket
        if not b:
            raise ValueError(
                    "You must specify a bucket in your request "
                    "or set the default_bucket for the connection")
        return b

    def _get_bucket_and_key(self, remote_name):
        if isinstance(remote_name, str):
            bucket = None
            key = remote_name
        elif isinstance(remote_name, S3Name):
            bucket = remote_name.bucket
            key = remote_name.key
        else:
            raise Exception, 'invalid remote_name: %s' % remote_name
        return self._get_bucket(bucket), key

class RemoteStoreError(Exception):
    pass 
    
class RemoteStore(object):
    """RemoteStore

API to remote storage
=====================

**ok = store.copy(remote_src, remote_dst, headers={})**
    Copy from remote store to remote store.  Used for renaming remote files or 
    updating their metadata.
**ok = store.delete(remote_name)**
    Delete file from remote store.
**exists, metadata = store.exists(remote_name)**
    Test if file exists in remote store and retrieve its metadata if it does.
**ok, metadata = store.read(remote_name, local_name)**
    Download a file from remote store and retrieve its metadata.
**ok = store.update_metadata(remote_name, headers)**
    Update a remote file's metadata.
**ok = store.write(local_name, remote_name, headers={})**
    Upload a file to remote store (and possibly set its metadata).

When a request is sent, the requests module may raise an exception or may
return status.  The status could indicate success or failure.  So there 
are 2 kinds of failure.  

All methods except **exists** catch connection exceptions, log either type of 
failure, and return True for success, and False for failure.

The **exists** method does not catch connection exceptions and may also raise 
RemoteStoreError.  It returns True or False as the remote_name exists in
remote storage or not.

**copy**, **update_metadata**, and **write** accept a headers argument which 
is used to provide additional headers to the request.

**exists** returns a tuple whose first element indicates if the file exists or 
not, and whose second element is the file's metadata (when the file exists).

**read** returns a tuple whose first element indicates success or failure and 
whose second element is the file's metadata (on success).

S3 Filenames
------------
An S3 file name consists of a bucket and a key.  This pair uniquely 
identifies the file within S3.  

The S3Connection class methods take a remote_name argument which can be 
either a string which is the key, or an instance of the S3Name class.  
When no bucket is given the default_bucket established when the connection 
is instantiated is used.

In other words, the S3Name class provides a means of using a bucket other 
than the default_bucket.

Headers and Metadata
--------------------

Additional http headers may be sent with the methods which write data.  These
control various aspects of how the file may be handled.  S3 supports a variety
of headers.  Those headers whose key begins with the special preifx:
'x-amz-meta-' are considered to be metadata headers and are used to set 
the metadata attributes of the file.
"""
    def __init__(self, connection, **kwargs):
        self.connection = connection

    def copy(self, remote_src, remote_dst, headers={}):
        """
        Copies remote_src to remote_dst.  headers may be used to change the 
        properties of remote_dst including its metadata.
        
        If any metadata headers are included in headers then they become the 
        metadata of remote_dst; otherwise the metadata of remote_src is copied.
        
        A metadata header is any header that starts with 
        `S3Facts.amz_metadata_prefix`
        
        Returns True/False => success/failure.
        In the event of failure, an error message is logged.
        """
        try:
            response = self.connection.copy(
                    remote_src, 
                    remote_dst, 
                    headers=headers)
            if not response.ok:
                logging.error(response.error)
            return response.ok

        except Exception, e:
            logging.exception(e)
            return False

    def delete(self, remote_name):
        """
        Deletes remote_name from the remote storage
        Returns True/False => success/failure.
        In the event of failure, an error message is logged.
        """
        try:
            response = self.connection.delete(remote_name)
            if not response.ok:
                logging.error(response.error)
            return response.ok

        except Exception, e:
            logging.exception(e)
            return False

    def exists(self, remote_name):
        """
        Tests if remote_name is stored in remote storage.
        Returns (exists, metadata)
            exists:  True if remote_name exists, False otherwise.
            metadata: the file's metadata (when exists == True)
        This method does not catch connection exceptions and may also throw 
        a RemoteStoreError exception.
        """
        response = self.connection.exists(remote_name)
        if response.ok:
            return not response.error, response.metadata
        else:
            raise RemoteStoreError, 'exists: %s' % response.error

    def read(self, remote_name, local_name):
        """
        Reads (downloads) `remote_name` from remote storage and saves it 
        in the local file system as `local_name`
        
        Returns (ok, metadata)
            ok:  True/False => success/failure.
                 In the event of failure, an error message is logged.
            metadata: the file's metadata (when ok == True)
        """
        try:
            timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
            tmp_filename = 's3-%s.tmp' % timestamp
            with open(tmp_filename, 'w+b') as fo:
                response = self.connection.read(remote_name, fo)
            if response.ok:
                os.rename(tmp_filename, local_name)
            else:
                logging.error(response.error)
            return response.ok, response.metadata
        except Exception, e:
            logging.exception(e)
            return False, {}

    def update_metadata(self, remote_name, headers):
        """
        Updates the properties of remote_name by including headers in the 
        request.

        Headers which begin with `S3Facts.amz_metadata_prefix` are used to
        set metadata.
        
        Returns True/False => success/failure.
        In the event of failure, an error message is logged.
        """
        try:
            response = self.connection.update_metadata(
                    remote_name,
                    headers=headers)
            if not response.ok:
                logging.error(response.error)
            return response.ok

        except Exception, e:
            logging.exception(e)
            return False

    def write(self, local_name, remote_name, headers={}):
        """
        Writes (uploads) `local_name` from the local file system to remote 
        storage as `remote_name`. `headers` may contain additional headers for 
        the request. 
        
        Headers which begin with `S3Facts.amz_metadata_prefix` are used to
        set metadata.
        
        Returns True/False => success/failure.
        In the event of failure, an error message is logged.
        """
        try:
            with open(local_name, 'r') as fi:
                response = self.connection.write(
                        fi, 
                        remote_name,
                        headers=headers)
            if not response.ok:
                logging.error(response.error)
            return response.ok
        except Exception, e:
            logging.exception(e)
            return False

