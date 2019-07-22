import asyncio
from rodio import EventLoop

process = EventLoop(block=False)


async def asyncfun1():
    print('asuncfun1 waiting 2 secs')
    await asyncio.sleep(2)
    print('asuncfun1 done waiting !')


async def asyncfun2():
    print('asuncfun2 waiting 2 secs')
    await asyncio.sleep(2)
    print('asuncfun2 done waiting !')


def queueAsyncFns():
    process.nextTick([asyncfun1, asyncfun2])


def actingfunction():
    print("helloworld")
    process.nextTick([queueAsyncFns, lambda: process.scheduleStop()])


print("before start")
process.nextTick(actingfunction)
print("after start")
