import sys
import posixpath as path
sys.path.append(path.normpath(path.join(path.dirname(__file__), '../..')))


def init():
    from rodio.internals.parther import getTransformer
    from rodio import EventLoop, printfromprocess

    tx = getTransformer(__file__)

    printfromprocess("__main__.py init")

    process1 = EventLoop("process1", self_pause=False)
    process2 = EventLoop("process2", self_pause=False)

    process1.load_module(tx('./module01.py'))
    process2.load_module(tx('./module02.py'))

    process1.kill()
    process2.kill()

    printfromprocess("__main__.py end")


init()
