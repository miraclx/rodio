import sys
from datetime import datetime


def hasArg(*args):
    return any(any(v.strip().endswith(x) for x in args) for v in sys.argv)


debugLoggers = {}


class LogDebugger:
    def __init__(self, identifier=None):
        if identifier in debugLoggers:
            raise ValueError(
                "The identifier for the debugger already exists within the stack")
        self.__debug_id__ = identifier
        self.__clearedToPrint = hasArg(
            '--DEBUG', *(f'--DEBUG={identifier}',) if identifier else ())
        debugLoggers[identifier] = self

    def log(self, fn, *args):
        if self.__clearedToPrint:
            print(f'[\x1b[33mDEBUG\x1b[0m@\x1b[34m{datetime.now().strftime("%T")}\x1b[0m] [\x1b[32m{fn}\x1b[0m]%s' % (
                f': {", ".join(map(str, args))}' if len(args) else ''))

    def debugwrapper(self, start=1, end=None):
        def wrapper(fn):
            def underlayer(*args, **kwargs):
                self.log(f'{fn.__qualname__}() init', *args[start:end])
                fn(*args, **kwargs)
                self.log(f'{fn.__qualname__}() exit')
            return underlayer
        if callable(start):
            [start, fn] = [1, start]
            return wrapper(fn)
        return wrapper


MainLogger = LogDebugger("")
debug = MainLogger.log
debugwrapper = MainLogger.debugwrapper
