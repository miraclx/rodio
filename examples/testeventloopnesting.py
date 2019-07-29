import os
from multiprocessing import Process
from rodio import EventLoop, printfromprocess, get_running_loop, is_within_loop


def buildEventLoop(count):
    if is_within_loop():
        parent = get_running_loop()
        printfromprocess(
            f"_is_directly_contained: {parent._is_directly_nested}")
    if count == 10:
        return
    process = EventLoop(f'process:{count}')
    process.nextTick(buildEventLoop, count + 1)
    process.scheduleExit()


buildEventLoop(1)
