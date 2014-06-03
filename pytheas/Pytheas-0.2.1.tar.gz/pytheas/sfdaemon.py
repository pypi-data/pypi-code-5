import gevent
import logging
import time

#from command_interpreter import PytheasCommandInterpreter
from errors import CorruptedCommunicationException, InvalidCommandException

#from gevent.lock import Semaphore
#from gevent.server import StreamServer

logging.basicConfig(filename="pytheas.log")
logger = logging.getLogger("pytheas")
logger.setLevel(logging.INFO)

class Pytheas(object):
    """
    Intended usage:
        Define your fetcher and sender classes (as extending from patterns.Fetcher
        and patterns.Sender). Then, create a Pytheas object from instances of
        those classes. Call the run method of this Pytheas object and you're set.
    """
    
    def __init__(self, fetcher, sender, sleep_time=1, command_interpreter=None, port=16981):
        """
        Instantiate a daemon object.

        fetcher -- A pytheas.patterns.Fetcher object.
        sender -- A pytheas.patters.Sender object.
        sleep_time -- Amount of sleep after every fetch/send iteration. Defaults
            to 1 second.
        command_interpreter -- Instance of command_interpreter.CommandInterpreter
            used to interpret commands sent to a running daemon.

            Note that Pytheas has a default command interpreter and should any
            of the user-defined commands conflict with Pytheas' command set,
            the Pytheas command will take precedence.
        port -- Port from which we listen for commands.
        """
        self.__fetcher = fetcher
        self.__sender = sender
        self.sleep_time = sleep_time
        #if port:
        #    self.__external_server = StreamServer(("127.0.0.0", port), self.__listen_external)
        #else:
        #    self.__external_server = None

        self.__ticket_counter = 1
        #self.__ticket_counter_lock = Semaphore()

        self.interpreter = command_interpreter
        #self.__default_interpreter = PytheasCommandInterpreter(self)

    def __sendfetch(self):
        self.__sender.send(self.__fetcher.fetch())
        gevent.sleep(1)

    def __listen_external(self, socket, address):
        """
        Sends two messages to any external client that has issued a command:
          - The first message is of the format "OK <ticketno>" where ticketno
            is a unique number identifying this transaction.
          - When it has finished processing the transaction and the processing
            is successful, it will send "T <ticketno>". Otherwise, send
            "F <ticketno>".

        All messages (commands and replies) are terminated by newlines (`\n`).
        """
        logger.info("external server received connection")
        # FIXME So the socket file is persistent? Why the while True? :\
        sockfile = socket.makefile()

        try:
            while True:
                command = sockfile.readline()
                logger.info("issued command " + command)
                if not command:
                    raise CorruptedCommunicationException(command)
                else:
                    ticketno = -1
                    self.__ticket_counter_lock.acquire()
                    ticketno = self.__ticket_counter
                    self.__ticket_counter += 1
                    self.__ticket_counter_lock.release()
                    sockfile.write("OK " + str(ticketno))
                    try:
                        if self.__default_interpreter.interpret_command(command):
                            sockfile.write("T" + str(ticketno))
                        else:
                            sockfile.write("F" + str(ticketno))
                    except ValueError, InvalidCommandException:
                        if self.interpreter.interpret_command(command):
                            sockfile.write("T" + str(ticketno))
                        else:
                            sockfile.write("F" + str(ticketno))
                    except:
                        break
        except e:
            logger.error("Encountered error while reading signal.", e)
        finally:
            sockfile.flush()

    def run(self):
        logger.info("Daemon started")
        
        while True:
            self.__sender.send(self.__fetcher.fetch())
            gevent.sleep(self.sleep_time)
