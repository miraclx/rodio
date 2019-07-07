# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import asyncio
import threading
from node_events import EventEmitter
from .eventqueue import EventQueue
from .internals.debug import debug, debugwrapper


class EventLoop(EventEmitter):
    _loop = _queue = _thread = __iteratorCoroutine = __autostarted = None

    @debugwrapper
    def __init__(self, name=None, *, autostart=True):
        self.name = name or 'asynceventloop'
        self._queue = EventQueue()
        self._loop = asyncio.get_event_loop()
        self._thread = threading.Thread(target=self.__initAsyncioLoop)
        self._thread._loop = self
        self._thread.setName(self.name)
        self.__autostart = autostart
        super(EventLoop, self).__init__()

    async def __asyncroot(self):
        debug('async __asyncroot init')
        await self._queue._startIterator()
        self.emit('exit')
        debug('async __asyncroot exit')

    def __initAsyncioLoop(self):
        asyncio.run(self.__asyncroot())

    @debugwrapper
    def nextTick(self, coro, *args):
        self._queue.put_nowait([coro, args])
        if self.__autostart and not self.started:
            self.start()
            self.__autostarted = True

    @debugwrapper
    def start(self):
        if self.__autostarted:
            raise RuntimeError("thread has been autostarted previously. assign %s on the EventLoop constructor to disable this"
                               % 'autostart=False')
        self._thread.start()

    @debugwrapper
    def join(self):
        if get_running_thread() is self._thread:
            raise self.__Error(RuntimeError(
                "Cannot join my process into myself, bro wassup"))
        self._thread.join()

    @debugwrapper
    def stop(self):
        self._queue.forceStop()

    @debugwrapper
    def __Error(self, err):
        self._queue.closeAll()
        return err

    @property
    def started(self):
        return self._thread._started.is_set()

    @property
    def ended(self):
        return self._queue.ended


def getRunningThread():
    return threading.current_thread()


def getRunningLoop(ret=None):
    loop = getattr(getRunningThread(), '_loop', None)
    if loop:
        return loop
    elif ret:
        return ret
    raise RuntimeError('no running event loop')


get_running_thread = getRunningThread
get_running_loop = getRunningLoop
