
import os
import sys

from kez.exceptions import *
from kez.utils import import_object

pathjoin = os.path.join
pathexists = os.path.exists

class status:
    PENDING = 1
    ERROR = 2
    SUCCESS = 3

class BuildController(object):

    def __init__(self, doctype, src, dst, options=None, settings=None):
        self.doctype = doctype
        self.src = src
        self.dst = dst
        self.options = options or {}
        self.settings = settings or {}
        self.logfile = pathjoin(self.dst, 'kez.log')
        self.status = None
        self.exc_info = None
        self._build_func = self._get_build_func()
        self._log = None

    def _get_build_func(self):
        func = 'kez.builders.' + self.doctype.lower() + '.build'
        try:
            return import_object(func)
        except ImportError:
            raise ConfigurationError("No builder for doctype '%s'" % self.doctype)

    def build(self, stdout=None, stderr=None):
        self.start()
        self.status = status.PENDING
        try:
            self._build_func(
                self.src, self.dst, self.options, self.settings, stdout, stderr
            )
        except Exception as e:
            self.status = status.ERROR
            self.exc_info = e
        else:
            self.status = status.SUCCESS
        finally:
            self.finish()

    def start(self):
        self._log = open(self.logfile, 'wb')

    def finish(self, **kw):
        try:
            self._log.close()
        except:
            pass


    def store_all(self, **kw):
        self.store_s3(**kw)

    def store_none(self, **kw):
        pass

    def store_s3(self, **kw):
        s3_bucket = kw.get(
            's3_bucket',
            getattr(settings, 'DOCHOUND_S3_BUCKET_NAME', None),
        )
        if not s3_bucket:
            raise DochoundBuildException("missing option 's3_bucket' or setting 'DOCHOUND_S3_BUCKET_NAME'")
        aws_access_key = kw.get(
            'aws_access_key',
            getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        )
        aws_secret_key = kw.get(
            'aws_secret_key',
            getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        )
        if not (aws_access_key and aws_secret_key):
            raise DochoundBuildException('missing AWS credentials')
        self._store_s3(
            s3_bucket,
            access_key=aws_access_key,
            secret_key=aws_secret_key
        )

    def _store_s3(self, bucketname, access_key, secret_key):
        bucket = S3Bucket(
            bucketname,
            access_key=access_key,
            secret_key=secret_key,
        )
        bucket.put_bucket(acl='public-read')
        root_url = self.doc.get_storage_key().lstrip('/')
        try:
            stored = set(t[0] for t in bucket.listdir(root_url))
        except:
            stored = set()
        for root, dirs, files in os.walk(self.outdir):
            dirs[:] = [d for d in dirs if d != '.doctrees']
            root = root.rstrip('/')
            relpath = root[len(self.outdir):]
            if relpath:
                relpath += '/'
            for f in files:
                src = root + '/' + f
                mimetype, encoding = mimetypes.guess_type(f)
                dest = root_url + relpath + f
                with open(src) as srcfile:
                    self.note('S3 PUT: %s' % dest)
                    bucket.put(dest, srcfile.read(), mimetype=mimetype, acl='public-read')
                try:
                    stored.remove(dest)
                except KeyError:
                    pass
        # remove everything from bucket that we haven't just uploaded
        for key in stored:
            self.note('S3 DELETE: %s' % key)
            bucket.delete(key)

