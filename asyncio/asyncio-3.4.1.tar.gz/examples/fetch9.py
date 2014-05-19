"""Simplest possible HTTP client."""

import sys

from asyncio import *


class Its:

    def __init__(self, stream):
        self._queue = Queue()
        async(self._feeder(stream))

    @coroutine
    def _feeder(self, stream):
        while True:
            line = yield from stream.readline()
            if not line:
                self._queue.put_nowait((False, None))
                break
            else:
                self._queue.put_nowait((True, line))

    @coroutine
    def more(self):
        flag, value = yield from self._queue.get()
        self.value = value
        return flag


@coroutine
def fetch():
    r, w = yield from open_connection('xkcd.com', 80)
    request = 'GET / HTTP/1.0\r\n\r\n'
    print('>', request, file=sys.stderr)
    w.write(request.encode('latin-1'))
    it = Its(r)
    while (yield from it.more()):
        line = it.value
        line = line.decode('latin-1')
        print(line, file=sys.stderr, end='')


def main():
    loop = get_event_loop()
    try:
        body = loop.run_until_complete(fetch())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
