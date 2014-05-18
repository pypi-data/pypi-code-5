
from exceptions import FileNotFound, FileTooLarge
from django.conf import settings
from cloudengine.files.backends.default import DefaultStorage


class FilesManager(object):
    
    def __init__(self, backend=DefaultStorage):
        self.backend = backend()
    
    def retrieve(self, filename, appobj):
        contents =  self.backend.retrieve(filename, appobj)
        if not contents:
            raise FileNotFound()
        return contents
                       
    def save(self, filename, uploaded_file, appobj):
        
        if uploaded_file.size > settings.MAX_FILESIZE:
            raise FileTooLarge()
        cloudfile = self.backend.save(filename, uploaded_file, appobj)
        return cloudfile
        
    def delete(self, filename, app):
        return self.backend.delete(filename, app)
        
        
