import os
from django.core.files.storage import default_storage
from django.conf import settings
from cloudengine.files.models import CloudFile
from cloudengine.files.exceptions import FileExists, FileNotFound

class DefaultStorage(object):
    """
    Default file storage which just saves files in specified folder 
    """
    
    def save(self, name, fileobj, app):
        "Upload a file"
        # Raise exception if a file with the filename already exists
        path = self.get_file_path(name, app)
        if default_storage.exists(path):
            raise FileExists()
        
        cloudfile = CloudFile(name=name, content=fileobj, 
                              size=fileobj.size, app=app)
        cloudfile.save()
        return cloudfile
    
    
    '''
    Since the file size is always smaller than what django can handle,
    read the contents in one go and return
    '''
    def retrieve(self, name, app):
        "Download a file"
        path = self.get_file_path(name, app)
        contents = None
        try:
            with open(path, "rb") as fp:
                contents = fp.read()
        except IOError:
            pass
        return contents
    
    def delete(self, name, app):
        path = self.get_file_path(name, app)
        if not default_storage.exists(path):
            raise FileNotFound()
        os.remove(path)
        cloudfile = CloudFile.objects.get(name=name, app=app)
        cloudfile.delete()
        
        
    def get_file_path(self, name, app):
        loc = settings.MEDIA_ROOT
        path = os.path.join(loc, app.name, name)
        return path
        
    