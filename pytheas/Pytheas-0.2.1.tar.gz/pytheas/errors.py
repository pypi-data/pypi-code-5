class InvalidCommandException(Exception):
    """
    Raised when we try to interpret an invalid command or a command that we
    cannot parse.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Received invalid command: " + str(self.value)

class CorruptedCommunicationException(InvalidCommandException):
    
    def __str__(self):
        return "Fatal corrupted command: " + str(self.value)
