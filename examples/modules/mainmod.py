from rodio.internals.parther import getTransformer
from rodio import get_running_loop, EventLoop, is_within_loop, printfromprocess

tx = getTransformer(__file__)

printfromprocess("mainmod.py init")
process1 = EventLoop(f"process1", self_pause=False, shared_queue=False)
process2 = EventLoop(f"process2", self_pause=False, shared_queue=False)

module1 = process1.load_module(tx('./module01.py'))
module2 = process2.load_module(tx('./module02.py'))

module1.on('complete', lambda process: (
    process.kill() if not process.ended() else None))

module2.on('complete', lambda process: (
    process.kill() if not process.ended() else None))

process1.join()
process2.join()

printfromprocess("mainmod.py exit")
