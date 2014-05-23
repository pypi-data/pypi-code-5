
class SiftError(Exception):

    def __init__(self, code, message=None):
        self.code = code
        self.message = message
        Exception.__init__(self, message, code)

class ServiceError(SiftError):

    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)


class InvalidCharactersInFieldValue(SiftError):
    pass
