import hashlib


class Md5Digest(object):
    """calculate a Md5 digest value for any combination of file contents given the file names and data strings.  does not read the entire file into memory at once"

        m = Md5Digest()
        m.addFile(".bashrc")
        m.addFile(".profile")
        m.addData("somerandomlineofdata")
        print m.digest


    """
    def __init__(self):
        self.md5 = hashlib.md5()


    def addFile(self,fileName):
        "based on code from  http://joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python/ "
        with open(fileName, 'rb') as fh:
            while True:
                data = fh.read(8192)
                if not data:
                    break
                self.md5.update(data) 

    def addData(self, data):
        self.md5.update(data)

    @property
    def digest(self):
        return self.md5.hexdigest()
