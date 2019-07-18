# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import threading
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


class EventLoop():
    _queue = _process = __block = __autostarted = __queued_exit = None

    @corelogger.debugwrapper
    def __init__(self, name=None, *, autostart=True, block=False, daemon=False):
        self.name = name or 'rodioeventloop'

        self.__block = block
        self.__autostart = autostart
        self.__queued_exit = threading.Event()

        self._queue = EventQueue()
        self._process = RodioProcess(target=self._run,  # Works with either RodioThread or RodioProcess
                                     name=self.name,
                                     daemon=daemon,
                                     killswitch=self._queue.end)
        setattr(self._process, '_eventloop', self)

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
            raise RuntimeError("EventLoop has been started already. Can't start a process beyond once%s"
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
    def pause(self):
        self._queue.pause()

    @corelogger.debugwrapper
    def resume(self):
        self._queue.resume()

    @corelogger.debugwrapper
    def scheduleStop(self):
        if self.ended():
            raise RuntimeError(
                "can't queue a process stop on an ended process")
        if self.end_is_queued():
            raise RuntimeError(
                "this process is already scheduled to stop")

        self.__queued_exit.set()
        self.nextTick(EventLoop.stop)

    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self.name = name
        self._process.set_name(self.name)

    setName = set_name

    def get_name(self):
        return self.name

    getName = get_name

    def started(self):
        return self._process.started()

    def ended(self):
        return self._process.ended() and self._queue.ended()

    def end_is_queued(self):
        return self.__queued_exit.is_set()

    def paused(self):
        return self._queue.paused()


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
