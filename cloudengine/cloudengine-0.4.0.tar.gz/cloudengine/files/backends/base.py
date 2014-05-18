


class BaseFileStorage(object):
    """
    Base storage class for different file storage backends. 
    """
    
    def save(self, name, fileobj):
        "Upload a file"
        raise NotImplementedError()
    
    def retrieve(self, name):
        "Download a file"
        raise NotImplementedError()
    
    def delete(self, name):
        "Delete a file"
        raise NotImplementedError()
    
    def rename(self, old_name, new_name):
        "Rename a file"
        raise NotImplementedError()
    