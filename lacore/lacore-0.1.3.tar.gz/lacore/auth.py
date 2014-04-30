import hashlib

from lacore.adf.elements import Auth


class MyHashObj(object):
    hashf = None

    def __init__(self, hashf='sha512'):
        self.md5 = hashlib.md5()
        if hasattr(hashlib, hashf):
            self.hashf = hashf
            setattr(self, hashf, getattr(hashlib, hashf)())

    def update(self, data):
        self.md5.update(data)
        if self.hashf:
            getattr(self, self.hashf).update(data)

    def auth(self):
        args = {'md5': self.md5.digest()}
        if self.hashf:
            args[self.hashf] = getattr(self, self.hashf).digest()
        return Auth(**args)

    def verify(self, auth):
        ret = (auth.md5 == self.md5.digest())
        if ret and self.hashf is not None:
            if hasattr(auth, self.hashf):
                h1 = getattr(self, self.hashf)
                h2 = getattr(auth, self.hashf)
                ret = (h1 == h2)
        return ret
