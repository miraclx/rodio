import sys
import posixpath as path
sys.path.append(path.normpath(path.join(path.dirname(__file__), '../..')))


def init():
    from rodio.internals.parther import getTransformer
    from rodio import EventLoop, printfromprocess

    tx = getTransformer(__file__)
    printfromprocess("__main__.py init")
    process = EventLoop("MainEventLoop", self_pause=False)
    process.load_module(tx('./mainmod.py'), block=True)
    process.terminate()
    printfromprocess("__main__.py end")


init()
