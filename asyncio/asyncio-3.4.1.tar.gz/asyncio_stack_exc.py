import asyncio


@asyncio.coroutine
def test_inner():
    yield from asyncio.sleep(0.1)

@asyncio.coroutine
def test_outer():
    t = asyncio.Task(test_inner())
    print('--begin--')
    t.print_stack()
    print('---end---')

loop = asyncio.get_event_loop()
loop.run_until_complete(test_outer())
