import asyncio
import urllib.parse
import sys

@asyncio.coroutine
def print_http_headers(url, timeout):
    url = urllib.parse.urlsplit(url)
    try:
        reader, writer = yield from asyncio.wait_for(asyncio.open_connection(url.hostname, 80), timeout)
    except asyncio.TimeoutError:
        print('Timed out with {}-second timeout'.format(timeout))
        return

    query = ('HEAD {url.path} HTTP/1.0\r\n'
             'Host: {url.hostname}\r\n'
             '\r\n').format(url=url)
    writer.write(query.encode('latin-1'))
    while True:
        line = yield from reader.readline()
        if not line:
            break
        line = line.decode('latin1').rstrip()
        if line:
            print('HTTP header> %s' % line)

    print('Success with {}-second timeout'.format(timeout))

url = sys.argv[1]
loop = asyncio.get_event_loop()

print('---start---')
for timeout in range(5, 0, -1):
    print('Attempt with timeout', timeout)
    task = asyncio.async(print_http_headers(url, timeout/100))
    loop.run_until_complete(task)

print('--close--')
loop.close()
print('---end---')
