import asyncio
import sys
from asyncio import async
import time
import random
asyncio.tasks._DEBUG = True


loop = asyncio.get_event_loop()

def read_something():
  print(input())

@asyncio.coroutine
def func(arg):
  while True:
    sys.stdout.write("\rtest"+str(arg))
    yield from asyncio.sleep(0)

loop.add_reader(sys.stdin, read_something)
loop.call_soon(async, func(1))
loop.call_soon(async, func(2))
loop.call_soon(async, func(3))
loop.call_soon(async, func(4))

time.sleep(1)

try:
  loop.run_forever()
except KeyboardInterrupt:
  print("handled\n")
  pass
finally:
  pass
