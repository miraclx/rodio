# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import dill
import queue
import asyncio
import multiprocessing
from node_events import EventEmitter
from .internals.debug import LogDebugger

__all__ = ['EventQueue']

corelogger = LogDebugger("rodiocore.eventqueue")


class EventQueue(EventEmitter):

    @corelogger.debugwrapper
    def __init__(self):
        super(EventQueue, self).__init__()
        self._ended = multiprocessing.Event()
        self._paused = multiprocessing.Event()
        self._running = multiprocessing.Event()
        self._statusLock = multiprocessing.RLock()
        self._underlayer = multiprocessing.JoinableQueue()

    @corelogger.debugwrapper
    def push(self, coro, args=()):
        if self.ended():
            raise RuntimeError(
                "Can't schedule executions on a stopped eventqueue")
        stack = list(coro if isinstance(coro, (tuple, list)) else [coro])
        notpassed = list(filter(lambda x: not callable(x), stack))
        if notpassed:
            raise RuntimeError(
                f"{notpassed} item{' defined must' if len(notpassed) == 1 else 's defined must all'} either be a coroutine function or a callable object")
        [stack, typeid] = self.__checkAll(asyncio.iscoroutinefunction, stack, [stack, 1]) or \
            self.__checkAll(callable, stack, [stack, 0])
        stack = dill.dumps(stack)
        self._underlayer.put([stack, args, typeid])
        self._resume()

    def __stripCoros(self):
        while not self.ended():
            try:
                self._running.wait()
                block = self._underlayer.get_nowait()
                self._underlayer.task_done()
                yield block
            except queue.Empty:
                if not self.ended():
                    self._pause()

    async def _startIterator(self):
        corelogger.log('async __startIterator init')
        for [stack, args, typeid] in self.__stripCoros():
            stack = dill.loads(stack)
            if typeid == 0:
                [fn(*args) for fn in stack]
            elif typeid == 1:
                await asyncio.gather(*[corofn(*args) for corofn in stack])
        corelogger.log('async __startIterator exit')

    @corelogger.debugwrapper
    def _resume(self):
        self._statusLock.acquire(True)
        self.__checkActivityElseRaise()
        self._paused.clear()
        self._running.set()
        self._statusLock.release()

    def start(self):
        self._resume()
        asyncio.run(self._startIterator())

    @corelogger.debugwrapper
    def resume(self):
        self._resume()
        self.emit('resume')

    def _pause(self):
        self._statusLock.acquire(True)
        self.__checkActivityElseRaise()
        self._paused.set()
        self._running.clear()
        self._statusLock.release()

    @corelogger.debugwrapper
    def pause(self):
        self._pause()
        self.emit('pause')

    def _end(self):
        self.__checkActivityElseRaise()
        self._running._cond.acquire()
        self._running._cond.notify()
        self._running._cond.release()
        self._ended.set()
        self._paused.clear()
        self._running.clear()

    @corelogger.debugwrapper
    def end(self):
        self._end()
        self.emit('end')

    def __checkActivityElseRaise(self):
        if self.ended():
            raise RuntimeError("Queue iterator already ended")

    def __checkAll(self, fn, iterable, ret=None, msg=None, permissive=True):
        gen = (fn(blob) for blob in iterable)
        if any(gen):
            if not all(gen):
                raise RuntimeError(
                    msg or 'A collection of executors must have the same type')
            else:
                return ret or True
        elif not permissive:
            raise RuntimeError(
                'Collection of executors must pass the condition')

    def paused(self):
        return self._paused.is_set() and not self._running.is_set()

    isPaused = paused
    is_paused = paused
    hasPaused = paused
    has_paused = paused

    def ended(self):
        return self._ended.is_set()

    isEnded = ended
    hasEnded = ended
    is_ended = ended
    has_ended = ended
