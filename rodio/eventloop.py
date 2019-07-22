# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import importlib
import threading
import multiprocessing
import posixpath as xpath
from .eventqueue import *
from .rodiothread import *
from .rodioprocess import *
from .internals.debug import LogDebugger

__all__ = ['EventLoop',
           'get_running_loop',
           'get_current_loop',
           'get_running_eventloop',
           'get_current_eventloop']

corelogger = LogDebugger("rodiocore.eventloop")


class LoopModuleStruct:
    def __init__(self, loop, path):
        self.path = path
        self.loader = importlib.machinery.SourceFileLoader(
            loop.get_name(), path)
        self.is_loaded = multiprocessing.Event()


class EventLoop():
    _name = _queue = _process = __block = __autostarted = __queued_exit = None

    @corelogger.debugwrapper
    def __init__(self, name=None, *, autostart=True, block=False, daemon=False):
        self._name = name or 'RodioEventLoop'
        self.__block = block
        self.__autostart = autostart
        self.__queued_exit = threading.Event()

        self._queue = EventQueue()
        self._process = RodioProcess(target=self._run,  # Works with either RodioThread or RodioProcess
                                     name=self._name,
                                     daemon=daemon,
                                     killswitch=self._queue.end)
        setattr(self._process, '_eventloop', self)

    def __repr__(self):
        status = []
        if self.started():
            status.append("started")
        if self.is_alive():
            status.append("alive")
        if not self.ended():
            status.append("paused" if self.paused() else "running")
        elif self.end_is_queued():
            status.append("ending")
        else:
            exitcode = self._process.exitcode
            status.append(
                f"stopped {f'[exitcode = {exitcode}]' if exitcode else ''}")
        return '<%s(%s, %s)>' % (type(self).__name__, self._name, ", ".join(status))

    def _run(self):
        self._queue.start()

    @corelogger.debugwrapper
    def nextTick(self, coro, *args):
        if self.ended():
            raise RuntimeError("Can't enqueue items to the ended process")
        if self.end_is_queued():
            raise RuntimeError(
                "Can't enqueue items to a process thats scheduled to stop")
        self._queue.push(coro, args)
        if self.__autostart and not self.started():
            self.start()
            self.__autostarted = True

    @corelogger.debugwrapper
    def start(self):
        if self.__autostarted:
            raise RuntimeError("EventLoop has been autostarted previously. assign %s on the EventLoop constructor to disable this"
                               % 'autostart=False')
        if self.started():
            raise RuntimeError("EventLoop has been previously started. They can only be started once%s"
                               % '')
        self._process.start()
        if self.__block:
            self.join()

    @corelogger.debugwrapper
    def join(self):
        if get_current_process() is self._process:
            raise RuntimeError(
                "You just tried to merge me and myself with my `join()` method... lol, you didn't mean that")
        self._process.join()

    @corelogger.debugwrapper
    def stop(self=None):
        process = self or getRunningLoop()
        process.__queued_exit.clear()
        process._process.stop()

    end = stop
    terminate = stop

    @corelogger.debugwrapper
    def pause(self=None):
        process = self or getRunningLoop()
        print(process, "queue.pause")
        process._queue.pause()

    @corelogger.debugwrapper
    def pause_process(self=None):
        process = self or getRunningLoop()
        print(process, "process.pause")
        process._process.pause()

    @corelogger.debugwrapper
    def resume(self):
        self._queue.resume()

    @corelogger.debugwrapper
    def resume_process(self):
        self._process.resume()

    @corelogger.debugwrapper
    def schedulePause(self):
        if self.ended():
            raise RuntimeError(
                "can't queue a queue pause on an ended process")
        self._queue.push(EventLoop.pause)

    @corelogger.debugwrapper
    def scheduleProcessPause(self):
        if self.ended():
            raise RuntimeError(
                "can't queue a process pause on an ended process")
        self._queue.push(EventLoop.pause_process)

    @corelogger.debugwrapper
    def scheduleStop(self):
        if self.ended():
            raise RuntimeError(
                "can't queue a process stop on an ended process")
        if self.end_is_queued():
            raise RuntimeError(
                "this process is already scheduled to stop")

        self.__queued_exit.set()
        self._queue.push(EventLoop.stop)

    @corelogger.debugwrapper
    def load_module(self, path: str, *, block=True):
        if not EventLoop.is_eventloop(self):
            raise TypeError("loop argument must be a valid EventLoop object")
        if self.ended():
            raise RuntimeError("Can't load a file under an ended eventloop")
        if isinstance(getattr(self, '_module_stack', None), LoopModuleStruct):
            raise RuntimeError(
                "This loop has already been attached a module, this can only be done once")
        struct = LoopModuleStruct(self, xpath.abspath(path))
        self._module_stack = struct

        def import_decoy():
            struct = get_running_loop()._module_stack
            struct.loader.load_module()
            struct.is_loaded.set()
        self.nextTick(import_decoy)
        if not block:
            return struct.is_loaded
        struct.is_loaded.wait()
        self._queue._paused.wait()

    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self._name = name
        self._process.set_name(self._name)

    setName = set_name

    def get_name(self):
        return self._name

    getName = get_name

    def started(self):
        return self._process.started()

    def is_alive(self):
        return self._process.is_alive()

    def ended(self):
        return self._process.ended() and self._queue.ended()

    def end_is_queued(self):
        return self.__queued_exit.is_set()

    def paused(self):
        return self._queue.paused() or self._process.paused()

    def __enter__(self):
        self.__with_exit_block = self.__block
        self.__block = False
        self.start()
        return self

    def __exit__(self, ttype, value, traceback):
        if self.__with_exit_block:
            self.join()
        return ttype is None

    @classmethod
    def is_eventloop(cls, loop):
        return isinstance(loop, cls)

# ========================================================

# Functions to get current event loop


def getRunningLoop(*args):
    loop = getattr(get_current_process(), '_eventloop', *args or (None,))
    if not (args or loop):
        raise RuntimeError('no running event loop')
    else:
        return loop


get_running_loop = getRunningLoop
get_current_loop = getRunningLoop

get_running_eventloop = getRunningLoop
get_current_eventloop = getRunningLoop

# ========================================================


"""

with EventLoop() as process:
    process.nextTick(exec1)
    process.nextTick(exec2)
    
print("hey")
"""
