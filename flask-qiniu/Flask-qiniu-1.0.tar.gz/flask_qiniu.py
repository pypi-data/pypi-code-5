import qiniu.rs
import qiniu.conf

class Qiniu(object):

    def __init__(self, app=None):
        self.app = app
        self._bucket = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("QINIU_ACCESS_KEY", None)
        app.config.setdefault("QINIU_SECRET_KEY", None)

        qiniu.conf.ACCESS_KEY = self.app.config['QINIU_ACCESS_KEY']
        qiniu.conf.SECRET_KEY = self.app.config['QINIU_SECRET_KEY']

        self._bucket = self.app.config['QINIU_BUCKET']

    @property
    def rs(self):
        return qiniu.rs

    @property
    def bucket(self):
        return self._bucket
