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
            idslot = f" (\x1b[36m{self.__debug_id__}\x1b[0m) " if hasArg(
                "--DEBUG-SHOW-ID") else " "
            print(f'[\x1b[33mDEBUG\x1b[0m@\x1b[34m{datetime.now().strftime("%T")}\x1b[0m]{idslot}[\x1b[32m{fn}\x1b[0m]%s' % (
                f': {", ".join(map(str, args))}' if len(args) else ''))

    def debugwrapper(self, start=1, end=None, fn_name=None):
        def wrapper(fn):
            xfn_name = fn_name or fn.__qualname__

            def underlayer(*args, **kwargs):
                self.log(f'{xfn_name}() init', *args[start:end])
                fn(*args, **kwargs)
                self.log(f'{xfn_name}() exit')
            return underlayer
        if callable(start):
            [start, fn] = [1, start]
            return wrapper(fn)
        if isinstance(start, str):
            [fn_name, start, end] = [start, end or 1, fn_name or end]
        return wrapper


MainLogger = LogDebugger("")
debug = MainLogger.log
debugwrapper = MainLogger.debugwrapper
