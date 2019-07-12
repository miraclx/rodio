# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import threading
from .eventqueue import EventQueue
from .rodiothread import RodioThread, current_thread
# from .rodioprocess import RodioProcess, current_process
from .internals.debug import debug, debugwrapper

__all__ = ['EventLoop',
           'get_running_loop',
           'get_current_loop',
           'getCurrentLoop',
           'getRunningEventloop',
           'get_running_eventloop',
           'getCurrentEventloop',
           'get_current_eventloop']


class EventLoop():
    _queue = _process = __block = __autostarted = __queued_exit = None

    @debugwrapper
    def __init__(self, name=None, *, autostart=True, block=False, daemon=False):
        self.name = name or 'rodioeventloop'

        self.__block = block
        self.__autostart = autostart
        self.__queued_exit = threading.Event()

        self._queue = EventQueue()
        self._process = RodioThread(target=self._run,  # Works with either RodioThread or RodioProcess
                                    name=self.name,
                                    daemon=daemon,
                                    killswitch=self._queue.end)
        self._process._eventloop = self

    def _run(self):
        self._queue.start()

    @debugwrapper
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

    @debugwrapper
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

    @debugwrapper
    def join(self):
        if current_thread() is self._process:
            raise RuntimeError(
                "Cannot join my process into itself, behave!")
        self._process.join()

    @debugwrapper
    def stop(self):
        self.__queued_exit.clear()
        self._process.stop()

    end = stop
    terminate = stop

    @debugwrapper
    def pause(self):
        self._queue.pause()

    @debugwrapper
    def resume(self):
        self._queue.resume()

    @debugwrapper
    def scheduleStop(self):
        if self.ended():
            raise RuntimeError(
                "can't queue a process stop on an ended process")
        if self.end_is_queued():
            raise RuntimeError(
                "this process is already scheduled to stop")
        self.nextTick(self.stop)
        self.__queued_exit.set()

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

# Functions to get the currently running process


get_running_process = current_thread
getRunningProcess = current_thread
get_current_process = current_thread
getCurrentProcess = current_thread

# ========================================================

# Functions to get current event loop


def getRunningLoop(*args):
    loop = getattr(current_thread(), '_eventloop', *args or (None,))
    if not (args or loop):
        raise RuntimeError('no running event loop')
    else:
        return loop


get_running_loop = getRunningLoop
get_current_loop = getRunningLoop
getCurrentLoop = getRunningLoop

getRunningEventloop = getRunningLoop
get_running_eventloop = getRunningLoop
getCurrentEventloop = getRunningLoop
get_current_eventloop = getRunningLoop

# ========================================================
"""

with EventLoop() as process:
    process.nextTick(exec1)
    process.nextTick(exec2)
    
print("hey")
"""
