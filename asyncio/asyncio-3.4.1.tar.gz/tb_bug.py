import asyncio
import gc
import logging

@asyncio.coroutine
def task(loop, fut):
    yield None
    try:
        raise RuntimeError()
    except Exception as exc:
        loop.call_soon(fut.set_exception, exc)
    fut = None
    loop = None

gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
logging.basicConfig()

loop = asyncio.get_event_loop()
#loop.set_debug(True)
fut = asyncio.Future(loop=loop)
loop.run_until_complete(task(loop, fut))
print(loop._ready)

fut = None
loop.run_until_complete(asyncio.sleep(0.01))
loop.close()

