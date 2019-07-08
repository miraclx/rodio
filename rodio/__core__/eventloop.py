# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import asyncio
from node_events import EventEmitter
from .eventqueue import EventQueue
from .rodioprocess import RodioProcess, get_current_process
from .internals.debug import debug, debugwrapper


class EventLoop(EventEmitter):
    _loop = _queue = _thread = __iteratorCoroutine = __autostarted = None

    @debugwrapper
    def __init__(self, name=None, *, autostart=True):
        super(EventLoop, self).__init__()
        self.name = name or 'asynceventloop'
        self.__autostart = autostart
        self._queue = EventQueue()
        self._process = RodioProcess(target=self._looper, name=self.name)
        self._process._eventloop = self

    async def __asyncroot(self):
        debug('async __asyncroot init')
        await self._queue._startIterator()
        self.emit('exit')
        debug('async __asyncroot exit')

    def __initAsyncioLoop(self):
        asyncio.run(self.__asyncroot())

    @debugwrapper
    def nextTick(self, coro, *args):
        self._queue.push(coro, args)
        if self.__autostart and not self.started:
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

    @debugwrapper
    def join(self):
        if get_running_process() is self._process:
            raise self.__closeAllBeforeRaise(RuntimeError(
                "Cannot join my process into itself, behave!"))
        self._process.join()

    @debugwrapper
    def stop(self):
        self._queue.forceStop()

    @debugwrapper
    def __closeAllBeforeRaise(self, err):
        self._queue.closeAll()
        return err

    @property
    def started(self):
        return self._process.has_started()

    @property
    def ended(self):
        return self._queue.ended

# ========================================================

# Functions to get the currently running process


get_running_process = get_current_process
getRunningProcess = get_current_process
get_current_process = get_current_process
getCurrentProcess = get_current_process

# ========================================================

# Functions to get current event loop


def getRunningLoop(ret=None):
    loop = getattr(get_current_process(), '_eventloop', None)
    if loop:
        return loop
    elif ret:
        return ret
    raise RuntimeError('no running event loop')


get_running_loop = getRunningLoop
get_current_loop = getRunningLoop
getCurrentLoop = getRunningLoop

getRunningEventloop = getRunningLoop
get_running_eventloop = getRunningLoop
getCurrentEventloop = getRunningLoop
get_current_eventloop = getRunningLoop

# ========================================================
