import asyncio
from rodio import get_running_loop, printfromprocess

process = get_running_loop()


async def act1():
    printfromprocess("act1 sleeping 2 secs")
    await asyncio.sleep(2)
    printfromprocess("act1 done sleeping 2 secs")


async def act2():
    printfromprocess("act2 sleeping 2 secs")
    await asyncio.sleep(2)
    printfromprocess("act2 done sleeping 2 secs")

process.nextTick(lambda: printfromprocess("module02.py init"))

process.nextTick(lambda: printfromprocess("lorem ipsum"))

process.nextTick([act1, act2])

process.nextTick(lambda: printfromprocess("dolor sit"))

process.nextTick(lambda: printfromprocess("amet consectur"))

process.nextTick(lambda: printfromprocess("module02.py exit"))
