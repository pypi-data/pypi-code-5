import sys
from twisted.internet.error import ReactorNotRunning
from twisted.python import log
from twisted.python.failure import Failure


def react(main, argv=(), _reactor=None):
    sys.stderr.write('Started reactor run')
    if _reactor is None:
        from twisted.internet import reactor as _reactor
    finished = main(_reactor, *argv)
    codes = [0]

    stopping = []
    _reactor.addSystemEventTrigger('before', 'shutdown', stopping.append, True)

    def stop(result, stopReactor):
        if stopReactor:
            try:
                _reactor.stop()
            except ReactorNotRunning:
                pass

        if isinstance(result, Failure):
            if result.check(SystemExit) is not None:
                code = result.value.code
            else:
                log.err(result, "main function encountered error")
                code = 1
            codes[0] = code

    def cbFinish(result):
        if stopping:
            stop(result, False)
        else:
            _reactor.callWhenRunning(stop, result, True)

    finished.addBoth(cbFinish)
    _reactor.run(False)
    sys.stderr.write('Finished reactor run')
