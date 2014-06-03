from errors import InvalidCommandException

import json
import re

class CommandInterpreter(object):
    """
    All command interpreters should extend from this class.
    """

    def interpret_command(self, data):
        """
        Performs some action based on the data.

        data -- Assumed as raw from the socket. This method will perform the
        necessary parsing.

        Returns True if the command was successfully executed. Otherwise, might
        raise InvalidCommandExceptions or return False.
        """
        raise NotImplementedException("This method should be implemented.")

class PytheasCommandInterpreter(CommandInterpreter):
    """
    Pytheas commands deal with on-the-spot reconfiguration of daemon properties.
    Pytheas commands have the following structure:
        
        {"set":<attribute>, "val":<new value>}
    """
    
    NUMERIC = re.compile(r"(\d*\.?)\d+")

    VALID_ATTRIBUTES = set(("sleep_time",))
    VALUE_VALIDATIONS = {"sleep_time": NUMERIC}
    
    
    def __init__(self, daemon):
        """
        Needs access to the daemon that will be using it.
        """
        self.daemon = daemon
   
    def interpret_command(self, data):
        command = json.loads(data)
        set_key = command.get("set")
        val_key = str(command.get("val"))
        
        if set_key and val_key:
            if set_key not in PytheasCommandInterpreter.VALID_ATTRIBUTES:
                raise InvalidCommandException(data)
            else:
                if PytheasCommandInterpreter.VALUE_VALIDATIONS[set_key].match(val_key):
                    if set_key == "sleep_time":
                        self.daemon.sleep_time = float(val_key) if "." in val_key else int(val_key)
                        return True
                else:
                    raise InvalidCommandException(data)
        else:
            raise InvalidCommandException(data)

        return False
