from collections import deque
import logging
from threading import Thread, Lock
import time


logging.basicConfig()
logger = logging.getLogger(__name__)
QUEUE_LOCK = Lock()


class HandlerPool(object):
    """
    Implements a threadpool for queuing and handling requests
    to the TCPServer.
    """

    def __init__(self, threads=4, poll_intv=0.001):
        # Create our task queue
        self.queue = deque()
        self.poll_intv = poll_intv

        # Mark as not finished
        self._shutdown = False

        # Start some threads
        self.workers = []
        for i in xrange(threads):
            t = Thread(target=self._worker)
            t.setDaemon(True)
            self.workers.append(t)
            t.start()

    def shutdown(self):
        "Waits for the pool to terminate"
        self._shutdown = True
        for t in self.workers:
            t.join()

    def add(self, handler):
        """
        Adds a handler to be executed.
        """
        self.queue.append(handler)

    def _worker(self):
        """ Worker main method.  Called to daemonize a thread.
        Continuously tries to pop request handlers off
        the queue and call their handle() method.
        """

        while True:
            try:
                with QUEUE_LOCK:
                    handler = self.queue.popleft()
            except IndexError:
                if self._shutdown:
                    break
                time.sleep(self.poll_intv)
                continue

            try:
                handler.handle()
            except Exception as e:
                msg = "Exception handling request!"
                msg = e.message if e.message else msg
                logger.error(msg)


REQUEST_QUEUE = None


def request_queue(workers=4, poll_intv=0.001):
    """
    Return an instance of a FIFO queue to which
    requests can be added.
    """
    global REQUEST_QUEUE
    if REQUEST_QUEUE is None:
        REQUEST_QUEUE = HandlerPool(workers, poll_intv)
    return REQUEST_QUEUE


