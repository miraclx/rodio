import asyncio
from rodio import EventLoop

process = EventLoop()


def normalfunction():
    print("normalfunction from within the eventloop")


async def normalasyncfunction1():
    print("normalasyncfunction1 called from within the eventloop")


async def normalasyncfunction2():
    print("normalasyncfunction2 called from within the eventloop")


async def awaitingasyncfunction1():
    print('awaitingasyncfunction1 will wait for 2 seconds')
    await asyncio.sleep(2)
    print('awaitingasyncfunction1 done waiting for 2 seconds')


async def awaitingasyncfunction2():
    print('awaitingasyncfunction2 will wait for 2 seconds')
    await asyncio.sleep(2)
    print('awaitingasyncfunction2 done waiting for 2 seconds')

print("=====================================================")

process.nextTick(normalfunction)
process.nextTick(normalasyncfunction1)
process.nextTick(normalasyncfunction2)
process.nextTick([
    awaitingasyncfunction1,
    awaitingasyncfunction2
])
process.nextTick(normalfunction)

process.scheduleStop()
