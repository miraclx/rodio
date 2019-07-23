# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import os
import signal
import multiprocessing
from .internals.debug import LogDebugger
from node_events import EventEmitter

__all__ = ['RodioProcess',
           'get_running_process',
           'get_current_process']


corelogger = LogDebugger("rodiocore.rodioprocess")


class RodioProcess(multiprocessing.context.Process, EventEmitter):
    _paused = _started = __killswitch = None

    @corelogger.debugwrapper
    def __init__(self, target, *, name=None, args=(), kwargs=None, daemon=None):
        super(RodioProcess, self).__init__(target=target,
                                           args=args or (),
                                           kwargs=kwargs or {},
                                           daemon=daemon)
        EventEmitter.__init__(self)

        self._started = multiprocessing.Event()
        self._paused = multiprocessing.Event()
        self._ended = multiprocessing.Event()
        self.set_name(name or self.name)



    @corelogger.debugwrapper
    def start(self):
        super(RodioProcess, self).start()
        self._started.set()

    def _pre_exit(self):
        if self.ended():
            raise RuntimeError("process already ended")
        if not self.started():
            raise RuntimeError("can't end a process before it starts")
        self.emit('beforeExit')
        
        self._paused.clear()

    def __pre_exit(self):
        self._pre_exit()
        self._ended.set()
        self.emit('exit')

    @corelogger.debugwrapper
    def terminate(self):
        self.__pre_exit()
        os.kill(self.pid, signal.SIGTERM)

    @corelogger.debugwrapper
    def kill(self):
        self.__pre_exit()
        os.kill(self.pid, signal.SIGKILL)

    def __pause(self, action, code):
        if not self.has_started():
            raise RuntimeError("unstarted process cant be paused")
        if self.ended():
            raise RuntimeError("can't pause ended process")
        if not self.paused():
            self._paused.set()
            if self.pid:
                os.kill(self.pid, code)
            else:
                raise RuntimeError("cant pause unstarted process")
        else:
            raise RuntimeError("process already paused")

    @corelogger.debugwrapper
    def pause(self):
        self.__pause('pause', signal.SIGTSTP)

    @corelogger.debugwrapper
    def halt(self):
        self.__pause('halt', signal.SIGSTOP)

    @corelogger.debugwrapper
    def resume(self):
        if not self.has_started():
            raise RuntimeError(
                "unstarted process can't be resumed because it couldn't be paused")
        if self.paused():
            self._paused.clear()
            os.kill(self.pid, signal.SIGCONT)
        else:
            raise RuntimeError("process not paused")

    def get_pid(self):
        return self.pid

    def ppid(self):
        return self._parent_pid

    get_ppid = ppid
    parent_pid = ppid

    @corelogger.debugwrapper
    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self.name = name

    setName = set_name

    def get_name(self):
        return self.name

    @corelogger.debugwrapper
    def set_daemon(self, state):
        if self.has_started:
            raise RuntimeError(
                "daemonizing process can only be done before initialization of process")
        if not isinstance(state, bool):
            raise TypeError("daemon state must be a boolean datatype")
        self.daemon = state

    def is_daemon(self):
        return self.daemon

    def started(self):
        return self._started.is_set()

    has_started = started

    def ended(self):
        return (self.has_started() and not self.is_alive()) or self._ended.is_set()

    has_ended = ended

    def is_zombie(self):
        return self.is_alive() and self.ended()

    def paused(self):
        return self._paused.is_set()

    has_paused = paused



def get_current_process():
    return multiprocessing.current_process()


get_running_process = get_current_process
