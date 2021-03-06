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
    def __init__(self, shared_queue=True):
        super(EventQueue, self).__init__()
        self.__shared_queue = bool(shared_queue)
        self._ended = multiprocessing.Event()
        self._started = multiprocessing.Event()
        self._paused = multiprocessing.Event()
        self._running = multiprocessing.Event()
        self._ended_or_paused = multiprocessing.Event()
        self._statusLock = multiprocessing.Lock()
        self._queueMgmtLock = multiprocessing.Lock()
        self._underlayer = queue.Queue(
        ) if not shared_queue else multiprocessing.JoinableQueue()
        self._pause()

    def __repr__(self):
        status = []
        if self.started():
            status.append("started")
        status.append("ended" if self.ended()
                      else "paused" if self.paused() else "running")
        status.append(f"{'' if self.is_shared() else 'un'}shared")
        status.append(f"[unfinished = {self._underlayer.qsize()}]" if self._underlayer.qsize(
        ) else "[complete]" if self.ended() else "[empty]")
        return '<%s(%s)>' % (type(self).__name__, ", ".join(status))

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
        if self.__shared_queue:
            stack = dill.dumps(stack)

        corelogger.log("push", "acquiring to push...")
        with self._queueMgmtLock:
            corelogger.log("push", "acquired to push")
            corelogger.log("push pre  put len", self._underlayer.qsize())
            self.emit('push', [stack, args])
            self._underlayer.put([stack, args, typeid])
            corelogger.log("push post put len", self._underlayer.qsize())
            corelogger.log("push", "strict resume")
            self._resume()

    def __stripCoros(self):
        while not self.ended():
            try:
                corelogger.log("__stripCoros", "acquiring to begin extract")
                if self._running.wait():
                    corelogger.log(
                        "__stripCoros", "acquired to begin extract!")
                    corelogger.log("__stripCoros", "acquiring to get...")
                    with self._queueMgmtLock:
                        corelogger.log("__stripCoros", "acquired to get")
                        if self._underlayer.qsize() == 0:
                            raise queue.Empty
                        corelogger.log("__stripCoros pre  get len",
                                       self._underlayer.qsize())
                        block = self._underlayer.get()
                        self.emit('get', block[:2])
                        corelogger.log("__stripCoros post get len",
                                       self._underlayer.qsize())
                        self._underlayer.task_done()
                    yield block
                else:
                    corelogger.log("__stripCoros", "run timeout")
            except queue.Empty:
                with self._queueMgmtLock:
                    corelogger.log("__stripCoros empty", "queue empty")
                    corelogger.log("__stripCoros empty get len",
                                   self._underlayer.qsize())
                    if not self.ended():
                        if self._underlayer.qsize() > 0:
                            corelogger.log(
                                "__stripCoros empty", "skipping pause after detecting items in queue")
                        else:
                            corelogger.log(
                                "__stripCoros empty", "pausing on queue empty")
                            self._pause()

    async def _startIterator(self):
        corelogger.log('async __startIterator init')
        for [stack, args, typeid] in self.__stripCoros():
            if self.__shared_queue:
                stack = dill.loads(stack)
            if typeid == 0:
                [fn(*args) for fn in stack]
            elif typeid == 1:
                await asyncio.gather(*[corofn(*args) for corofn in stack])
        corelogger.log('async __startIterator exit')

    @corelogger.debugwrapper
    def _resume(self):
        self.__checkActivityElseRaise()
        corelogger.log("_resume", "acquiring to resume...")
        with self._statusLock:
            corelogger.log("_resume", "acquired to resume")
            self._paused.clear()
            self._running.set()
            self._ended_or_paused.clear()

    def start(self):
        self._started.set()
        self.emit('start')
        self._resume()
        asyncio.run(self._startIterator())

    @corelogger.debugwrapper
    def resume(self):
        self._resume()
        self.emit('resume')

    def _pause(self):
        self.__checkActivityElseRaise()
        corelogger.log("_pause", "acquiring to pause...")
        with self._statusLock:
            corelogger.log("_pause", "acquired to pause")
            self._paused.set()
            self._running.clear()
            self._ended_or_paused.set()

    @corelogger.debugwrapper
    def pause(self):
        self._pause()
        self.emit('pause')

    def _end(self):
        self.__checkActivityElseRaise()
        with self._running._cond:
            self._running._cond.notify()
        self._ended.set()
        self._paused.clear()
        self._running.clear()
        self._ended_or_paused.set()

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

    is_paused = paused
    has_paused = paused

    def started(self):
        return self._started.is_set()

    def ended(self):
        return self._ended.is_set()

    def is_shared(self):
        return self.__shared_queue

    is_ended = ended
    has_ended = ended
