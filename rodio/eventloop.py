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
from node_events import EventEmitter

__all__ = ['EventLoop',
           'is_within_loop',
           'get_running_loop',
           'get_current_loop']

corelogger = LogDebugger("rodiocore.eventloop")


class LoopModuleStruct(EventEmitter):
    def __init__(self, loop, path):
        super(LoopModuleStruct, self).__init__()
        self.path = path
        self.loop = loop
        self.loader = importlib.machinery.SourceFileLoader(
            loop.get_name(), path)
        self.is_loaded = multiprocessing.Event()

    def init(self):
        self.loop._queue.once('end', self.is_loaded.set)
        self.loader.load_module()
        self.is_loaded.set()

    def wait(self, block=False, event_queue=[]):
        def target():
            self.is_loaded.wait()
            self.emit('loaded')
            for [eventname, ret, raw_event] in event_queue:
                raw_event.wait()
                self.emit(eventname, ret)

        thandle = threading.Thread(target=target)
        thandle.start()
        thandle.join() if block else None
        return self


class EventLoop(EventEmitter):
    _name = _queue = _process = __block = __autostarted = __queued_exit = None

    @corelogger.debugwrapper
    def __init__(self, name=None, *, autostart=True, block=False, daemon=False, self_pause=True):
        self._name = name or 'RodioEventLoop'
        self.__block = block
        self.__autostart = autostart
        self.__self_pause = self_pause
        self.__queued_exit = threading.Event()

        self._queue = EventQueue()
        self._process = RodioProcess(target=self._run,
                                     name=self._name,
                                     daemon=daemon)
        self._process.on('beforeExit', self._onend)
        setattr(self._process, '_eventloop', self)
        super(EventLoop, self).__init__()

    def __repr__(self):
        status = []
        if self.started():
            status.append("started")
        if self.is_active():
            status.append("active")
        if not self.ended():
            status.append("paused" if self.paused() else "running")
        elif self.end_is_queued():
            status.append("ending")
        else:
            exitcode = self._process.exitcode
            status.append(
                f"stopped{f' [exitcode = {exitcode}]' if isinstance(exitcode, (int, float)) else ''}")
        return '<%s(%s, %s)>' % (type(self).__name__, self._name, ", ".join(status))

    def _run(self):
        try:
            self._queue.start()
        except SystemExit as e:
            self._exit(1 if not e.args else e.args[0] or 0)

    def _onend(self):
        self.emit('beforeExit')
        self._queue.end()

    @corelogger.debugwrapper
    def nextTick(self, coro, *args):
        if self.ended():
            raise RuntimeError("Can't enqueue items to the ended process")
        if self.end_is_queued():
            raise RuntimeError(
                "Can't enqueue items to a process thats scheduled to stop")
        self.emit('nextTick', [coro, args])
        self._queue.push(coro, args)
        if self.__autostart and not self.started():
            self.emit('autostart')
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
        self.emit('start')
        self._process.start()
        if self.__block:
            self.join()

    @corelogger.debugwrapper
    def join(self):
        if get_current_process() is self._process:
            raise RuntimeError(
                "You just tried to merge me and myself with my `join()` method... lol, you didn't mean that%s"
                % '')
        self.emit('join')
        self._process.join()

    @corelogger.debugwrapper
    def kill(self=None):
        process = check_or_get_loop(self)
        process.__queued_exit.clear()
        self.emit('kill')
        process._process.kill()

    @corelogger.debugwrapper
    def terminate(self=None):
        process = check_or_get_loop(self)
        process.__queued_exit.clear()
        self.emit('terminate')
        process._process.terminate()

    @corelogger.debugwrapper
    def _exit(self=None, code=0):
        process = check_or_get_loop(self)
        if not get_running_loop(None) is process:
            raise RuntimeError(
                "exit() should only be called from self process")
        process.__queued_exit.clear()
        process._process._pre_exit()
        self.emit('exit')
        exit(code)

    @corelogger.debugwrapper
    def exit(self=None, code=0):
        process = check_or_get_loop(self)
        if not get_running_loop(None) is process:
            raise RuntimeError(
                "exit() should only be called from self process")
        exit(code)

    def __raiseIfNotSelfPausable(self):
        if get_running_loop(None) is self and not self.__self_pause:
            raise RuntimeError(
                f"can't pause the eventloop named [{self.get_name()}] from within it's process%s"
                % '')

    @corelogger.debugwrapper
    def pause(self=None):
        process = check_or_get_loop(self)
        process.__raiseIfNotSelfPausable()
        self.emit('pause')
        process._queue.pause()

    @corelogger.debugwrapper
    def pause_process(self=None):
        process = check_or_get_loop(self)
        process.__raiseIfNotSelfPausable()
        self.emit('processpause')
        process._process.pause()

    @corelogger.debugwrapper
    def resume(self):
        self.emit('resume')
        self._queue.resume()

    @corelogger.debugwrapper
    def resume_process(self):
        self.emit('resumeprocess')
        self._process.resume()

    def scheduler(self, method, *, name=None, fn=None, fns=[], event=None, end_message=None, exec_checks=[]):
        fns.append(fn) if fn else None
        @corelogger.debugwrapper(name)
        def deployed_fn(self, *args, **kwargs):
            if self.ended():
                raise RuntimeError(
                    end_message or f"can't execute {name or 'scheduled method'} on an ended process")
            for slot in exec_checks:
                if slot[0](self):
                    raise slot[1]
            [fn(self, *args, **kwargs) for fn in fns]
            self.emit(event) if event else None
            self._queue.push(method)
        deployed_fn.__name__ = deployed_fn.__name__.replace(
            deployed_fn.__name__, name)
        deployed_fn.__qualname__ = deployed_fn.__qualname__.replace(
            deployed_fn.__name__, name)
        return deployed_fn

    schedulePause = scheduler(None, pause, name='schedulePause', event='schedulePause',
                              end_message="can't queue a queue pause on an ended process")

    scheduleProcessPause = scheduler(None, pause_process, name='scheduleProcessPause', event='scheduleProcessPause',
                                     end_message="can't queue a process pause on an ended process")

    scheduleExit = scheduler(None, exit,
                             name='scheduleExit', event='scheduleExit',
                             fn=lambda self: self.__queued_exit.set(),
                             exec_checks=[
                                 [
                                     lambda self: self.end_is_queued(),
                                     RuntimeError(
                                         "this process is already scheduled to stop")
                                 ]
                             ])

    scheduleTERM = scheduler(None, terminate,
                             name='scheduleTERM', event='scheduleTERM',
                             fn=lambda self: self.__queued_exit.set(),
                             exec_checks=[
                                 [
                                     lambda self: self.end_is_queued(),
                                     RuntimeError(
                                         "this process is already scheduled to stop")
                                 ]
                             ])

    scheduleKILL = scheduler(None, kill,
                             name='scheduleKILL', event='scheduleKILL',
                             fn=lambda self: self.__queued_exit.set(),
                             exec_checks=[
                                 [
                                     lambda self: self.end_is_queued(),
                                     RuntimeError(
                                         "this process is already scheduled to stop")
                                 ]
                             ])

    @corelogger.debugwrapper
    def load_module(self, path: str, *, block=False):
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
            loop = get_running_loop()
            struct = loop._module_stack
            loop._queue.once('end', struct.is_loaded.set)
            struct.loader.load_module()
            struct.is_loaded.set()
        self.nextTick(import_decoy)
        return struct.init(block=block, event_queue=[
            ['complete', self, self._queue._ended_or_paused]
        ])

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

    def is_active(self):
        return self._process.is_active() and not self._queue.ended()

    def ended(self):
        return self._process.ended() or self._queue.ended()

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


def is_within_loop() -> bool:
    return bool(getattr(get_current_process(), '_eventloop', None))


def get_current_loop(*args):
    loop: EventLoop = getattr(get_current_process(),
                              '_eventloop', *args or (None,))
    if not (args or loop):
        raise RuntimeError('no running event loop')
    else:
        return loop


get_running_loop = get_current_loop


def check_or_get_loop(input=None):
    ret = input or get_running_loop(None)
    if isinstance(ret, EventLoop):
        return ret
    if input:
        raise TypeError("input argument, if defined must be EventLoop")
    raise RuntimeError("no event loop is defined or running")

# ========================================================
