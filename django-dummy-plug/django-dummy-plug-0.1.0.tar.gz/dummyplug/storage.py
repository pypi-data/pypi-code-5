from django.core.files.storage import Storage


class IOErrorStorage(Storage):
    def _get(self, name):
        raise IOError

    def _open(self, name, mode='rb'):
        raise IOError

    def _save(self, name, content):
        raise IOError

    def delete(self, name):
        raise IOError

    def exists(self, name):
        raise IOError

    def listdir(self, path):
        raise IOError

    def size(self, name):
        raise IOError
