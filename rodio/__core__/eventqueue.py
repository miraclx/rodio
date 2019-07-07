# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import asyncio
from .internals.debug import debug, debugwrapper


class EventQueue(asyncio.Queue):
    __forceIterStop = __ended = False
    @debugwrapper
    def __init__(self):
        super(EventQueue, self).__init__()

    @debugwrapper
    def push(self, block):
        self.put_nowait(block)

    async def __stripCoros(self):
        debug('async __stripCoros init')
        while not self.empty() and not self.ended:
            yield await self.get()
        self.__ended = True
        debug('async __stripCoros exit')

    async def _startIterator(self):
        debug('async __startIterator init')
        async for [coro, args] in self.__stripCoros():
            await coro if asyncio.iscoroutine(coro) else await coro(*args) if asyncio.iscoroutinefunction(coro) else await asyncio.gather(*coro) if isinstance(coro, (list, tuple)) else coro(*args)
            self.task_done()
        debug('async __startIterator exit')

    @debugwrapper
    def forceStop(self):
        if self.__ended:
            raise RuntimeError("Queue iterator already ended")
        if self.__forceIterStop:
            raise RuntimeError("Queue iterator already force-stopped")
        self.__forceIterStop = self.__ended = True

    def closeAll(self):
        self._queue.clear()

    @property
    def ended(self):
        return self.__ended or self.__forceIterStop
