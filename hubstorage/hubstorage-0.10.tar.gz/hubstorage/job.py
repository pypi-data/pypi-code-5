import logging
from .resourcetype import ItemsResourceType, MappingResourceType
from .utils import millitime, urlpathjoin
from .jobq import JobQ


class Job(object):

    def __init__(self, client, key, auth=None, jobauth=None, metadata=None):
        self.key = urlpathjoin(key)
        assert len(self.key.split('/')) == 3, 'Jobkey must be projectid/spiderid/jobid: %s' % self.key
        self._jobauth = jobauth
        # It can't use self.jobauth because metadata is not ready yet
        self.auth = jobauth or auth
        self.metadata = JobMeta(client, self.key, self.auth, cached=metadata)
        self.items = Items(client, self.key, self.auth)
        self.logs = Logs(client, self.key, self.auth)
        self.samples = Samples(client, self.key, self.auth)
        self.requests = Requests(client, self.key, self.auth)
        self.jobq = JobQ(client, self.key.split('/')[0], auth)

    def close_writers(self):
        wl = [self.items, self.logs, self.samples, self.requests]
        # close all resources that use background writers
        for w in wl:
            w.close(block=False)
        # now wait for all writers to close together
        for w in wl:
            w.close(block=True)

    @property
    def jobauth(self):
        if self._jobauth is None:
            token = self.metadata.authtoken()
            self._jobauth = (self.key, token)
        return self._jobauth

    def _update_metadata(self, *args, **kwargs):
        self.metadata.update(*args, **kwargs)
        self.metadata.save()
        self.metadata.expire()

    def request_cancel(self):
        self.jobq.request_cancel(self)

    def finished(self, close_reason=None):
        self.metadata.expire()
        close_reason = close_reason or \
            self.metadata.liveget('close_reason') or 'no_reason'
        self._update_metadata(close_reason=close_reason)
        self.close_writers()
        self.jobq.finish(self)

    def failed(self, reason='failed', message=None):
        if message:
            self.logs.error(message, appendmode=True)
        self.finished(reason)

    def purged(self):
        self.jobq.delete(self)
        self.metadata.expire()

    def stop(self):
        self._update_metadata(stop_requested=True)


class JobMeta(MappingResourceType):

    resource_type = 'jobs'
    ignore_fields = set(('auth', '_key', 'state'))

    def authtoken(self):
        return self.liveget('auth')


class Logs(ItemsResourceType):

    resource_type = 'logs'
    batch_content_encoding = 'gzip'

    def log(self, message, level=logging.INFO, ts=None, appendmode=False, **other):
        other.update(message=message, level=level, time=ts or millitime())
        if self._writer is None:
            self.batch_append = appendmode
        self.write(other)

    def debug(self, message, **other):
        self.log(message, level=logging.DEBUG, **other)

    def info(self, message, **other):
        self.log(message, level=logging.INFO, **other)

    def warn(self, message, **other):
        self.log(message, level=logging.WARNING, **other)
    warning = warn

    def error(self, message, **other):
        self.log(message, level=logging.ERROR, **other)


class Items(ItemsResourceType):

    resource_type = 'items'
    batch_content_encoding = 'gzip'


class Samples(ItemsResourceType):

    resource_type = 'samples'

    def stats(self):
        raise NotImplementedError('Resource does not expose stats')


class Requests(ItemsResourceType):

    resource_type = 'requests'
    batch_content_encoding = 'gzip'

    def add(self, url, status, method, rs, parent, duration, ts, fp=None):
        return self.write({
            'url': url,
            'status': int(status),
            'method': method,
            'rs': int(rs),
            'duration': int(duration),
            'parent': parent,
            'time': int(ts),
            'fp': fp,
        })
