#!/usr/bin/env python
 
"""
When PYTHONASYNCIODEBUG is set to 1, this causes a strange error:
 
TypeError: send() takes 2 positional arguments but 7 were given
 
Invoke as follows:
 
$ PYTHONASYNCIODEBUG=1 python3 put_get_bug.py
 
Note that os.environ["PYTHONASYNCIODEBUG"] = "1" doesn't work.
"""
 
import asyncio
import os
 
@asyncio.coroutine
def t1(q):
    yield from asyncio.sleep(0.5)
    print('t1: put(blah)')
    q.put_nowait((0, 1, 2, 3, 4, 5))
    print('t1: done')
 
@asyncio.coroutine
def t2(q):
    print('t2: get()')
    f = q.get()
    print('t2: f =', repr(f))
    v = yield from f
    print('t2: v =', repr(v))

def main():
    q = asyncio.Queue()
    done, pend = asyncio.get_event_loop().run_until_complete(asyncio.wait([t1(q), t2(q)]))
    print('main: done =', repr(done), '; pend =', repr(pend))

main()

