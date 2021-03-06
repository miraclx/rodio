import sys
import rodio
from datetime import datetime


"""
CLi Arguments
--DEBUG: Show Debug Information
--DEBUG=<id>: Show Specific Debug Information
--DEBUG-SHOW-ID: Show debugger id when printing
--DEBUG-SHOW-PROCESS: Show Current Process Name at the Time of log
"""


def hasArg(*args):
    return any(any(v.strip().endswith(x) for x in args) for v in sys.argv)


debugLoggers = {}


class LogDebugger:
    def __init__(self, identifier=None):
        if identifier in debugLoggers:
            raise ValueError(
                "The identifier for the debugger already exists within the stack")
        self.__debug_id__ = identifier
        self.__printer = rodio.printfromprocess if hasArg(
            '--DEBUG-SHOW-PROCESS') else print
        self.__clearedToPrint = hasArg(
            '--DEBUG', *(f'--DEBUG={identifier}',) if identifier else ())
        debugLoggers[identifier] = self

    def log(self, fn, *args):
        if self.__clearedToPrint:
            idslot = f" (\x1b[36m{self.__debug_id__}\x1b[0m) " if hasArg(
                "--DEBUG-SHOW-ID") else " "
            self.__printer(f'[\x1b[33mDEBUG\x1b[0m@\x1b[34m{datetime.now().strftime("%T")}\x1b[0m]{idslot}[\x1b[32m{fn}\x1b[0m]%s' % (
                f': {", ".join(map(str, args))}' if len(args) else ''))

    def debugwrapper(self, start=1, end=None, fn_name=None):
        def wrapper(fn):
            xfn_name = fn_name or fn.__qualname__

            def underlayer(*args, **kwargs):
                self.log(f'{xfn_name}() init', *args[start:end])
                ret = \
                    fn(*args, **kwargs)  # THIS IS A DECOY FUNCTION!, IF DEBUGGING, THE FUNCTION ABOVE IS THE ACTUAL ONE
                self.log(f'{xfn_name}() exit')
                return ret
            underlayer.__name__ = fn.__name__
            underlayer.__qualname__ = fn.__qualname__
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
