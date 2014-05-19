#!/usr/bin/env python
 
"""
When PYTHONASYNCIODEBUG is set to 1, this causes a strange error:
 
TypeError: send() takes 2 positional arguments but 7 were given
 
Invoke as follows:
 
$ PYTHONASYNCIODEBUG=1 python3 put_get_bug.py
 
Note that os.environ["PYTHONASYNCIODEBUG"] = "1" doesn't work.
"""

import asyncio
import builtins
import os
import sys
import time

T0 = time.time()

## def print(*args, file=None, end='\n'):
##     if file is None:
##         file = sys.stdout
##     s = ' '.join(map(str, args))
##     file.write('T=%.3f: %s%s' % (time.time() - T0, s, end))

## builtins.print = print

def t1(q):
    print('t1 starting')
    yield from asyncio.sleep(0.5)
    print('t1 waking up')
    q.put_nowait((0, 1, 2, 3, 4, 5))
    print('t1 done')
 
def t2(q):
    print('t2 starting')
    v = yield from q.get()
    print('t2 got value', repr(v))

def main():
    print('main starting')
    q = asyncio.Queue()
    done, pend = asyncio.get_event_loop().run_until_complete(asyncio.wait([t1(q), t2(q)]))
    print('done =', repr(done))
    print('pend =', repr(pend))

main()
