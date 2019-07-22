import asyncio
from rodio import get_running_loop, printfromprocess

process = get_running_loop()


def normalfunction():
    printfromprocess("normalfunction from within the eventloop")


async def normalasyncfunction1():
    printfromprocess("normalasyncfunction1 called from within the eventloop")


async def normalasyncfunction2():
    printfromprocess("normalasyncfunction2 called from within the eventloop")


async def awaitingasyncfunction1():
    printfromprocess('awaitingasyncfunction1 will wait for 2 seconds')
    await asyncio.sleep(2)
    printfromprocess('awaitingasyncfunction1 done waiting for 2 seconds')


async def awaitingasyncfunction2():
    printfromprocess('awaitingasyncfunction2 will wait for 2 seconds')
    await asyncio.sleep(2)
    printfromprocess('awaitingasyncfunction2 done waiting for 2 seconds')

process.nextTick(normalfunction)
process.nextTick(normalasyncfunction1)
process.nextTick(normalasyncfunction2)
process.nextTick([
    awaitingasyncfunction1,
    awaitingasyncfunction2
])
process.nextTick(normalfunction)
