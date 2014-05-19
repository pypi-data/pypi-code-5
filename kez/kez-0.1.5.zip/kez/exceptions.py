
class URLFormatError(Exception):
    pass

class ObjectExistsError(Exception):
    pass

class MultipleObjectsReturnedError(Exception):
    pass

class MissingOrInvalidConfig(Exception):
    pass

class ConfigurationError(Exception):
    pass

class UnknownBuilderError(Exception):
    pass

class UnknownDocumentError(Exception):
    
    def __init__(self, project, docname):
        msg = "Unknown document '%s' in project '%s'" % (docname, project)
        super(UnknownDocumentError, self).__init__(msg)

class NoDocumentIndexError(Exception):
    pass

