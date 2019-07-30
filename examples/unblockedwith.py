
import time
from rodio import EventLoop, get_current_loop, printfromprocess


def decoy():
    loop = get_current_loop()
    printfromprocess("heyyo from decoy")
    printfromprocess("sleeping for 2 secs...")
    time.sleep(2)
    printfromprocess("quiting after 3 secs...")
    time.sleep(3)
    loop.scheduleExit()


printfromprocess("main init")

with EventLoop(block=False) as loop:
    loop.nextTick(lambda: printfromprocess("hello"))
    loop.nextTick(lambda: printfromprocess("world"))
    loop.nextTick(decoy)


printfromprocess("main exit")
