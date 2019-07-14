# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import os
import signal
import multiprocessing
from .internals.debug import debug, debugwrapper

__all__ = ['RodioProcess',
           'get_running_process',
           'getRunningProcess',
           'get_current_process',
           'getCurrentProcess']


class RodioProcess(multiprocessing.context.Process):

    @debugwrapper
    def __init__(self, target, *, name=None, args=(), kwargs=None, daemon=None, killswitch=None):
        super(RodioProcess, self).__init__(target=target,
                                           args=args or (),
                                           kwargs=kwargs or {},
                                           daemon=daemon)

        self.__killswitch = killswitch

        self._started = multiprocessing.Event()
        self._paused = multiprocessing.Event()
        self.set_name(name or self.name)

    @debugwrapper
    def start(self):
        multiprocessing.process.BaseProcess.start(self)
        self._started.set()

    init = start

    def __preexit(self):
        if self.ended():
            raise RuntimeError("process already ended")
        if self.__killswitch:
            self.__killswitch()

    @debugwrapper
    def stop(self):
        self.__preexit()
        multiprocessing.process.BaseProcess.terminate(self)

    end = stop
    terminate = stop

    @debugwrapper
    def kill(self):
        self.__preexit()
        multiprocessing.process.BaseProcess.kill(self)

    def __pause(self, action, code):
        if not self.has_started():
            raise RuntimeError("unstarted process cant be paused")
        if self.ended():
            raise RuntimeError("can't pause ended process")
        if not self.paused():
            # self.__checkNotSelfProcess(
            #     msg="cant pause process while within itself")
            self._paused.set()
            if self.pid:
                os.kill(self.pid, code)
            else:
                raise RuntimeError("cant pause unstarted process")
        else:
            raise RuntimeError("process already paused")

    @debugwrapper
    def pause(self):
        self.__pause('pause', signal.SIGTSTP)

    @debugwrapper
    def halt(self):
        self.__pause('halt', signal.SIGSTOP)

    @debugwrapper
    def resume(self):
        if not self.has_started():
            raise RuntimeError(
                "unstarted process can't be resumed because it couldn't be paused")
        if self.paused():
            self.__checkNotSelfProcess(
                self, msg="cant pause process while within itself")
            self._paused.clear()
            os.kill(self.pid, signal.SIGCONT)
        else:
            raise RuntimeError("process not paused")

    def get_pid(self):
        return self.pid

    getPid = get_pid

    def ppid(self):
        return self._parent_pid

    get_ppid = ppid
    getPpid = ppid
    get_parentpid = ppid
    parent_pid = ppid
    parentPid = ppid

    @debugwrapper
    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self.name = name

    setName = set_name

    def get_name(self):
        return self.name

    getName = get_name

    @debugwrapper
    def set_daemon(self, state):
        if self.has_started:
            raise RuntimeError(
                "daemonizing process can only be done before initialization of process")
        if not isinstance(state, bool):
            raise TypeError("daemon state must be a boolean datatype")
        self.daemon = state

    setDaemon = set_daemon

    def is_daemon(self):
        return self.daemon

    isDaemon = is_daemon

    def started(self):
        return self.is_alive() and self._started.is_set()

    has_started = started
    hasStarted = started

    def ended(self):
        return self.has_started and not self.is_alive()

    has_ended = ended
    hasEnded = ended

    def paused(self):
        return self._paused.is_set()

    has_paused = paused
    hasPaused = paused

    def __checkNotSelfProcess(self, ret=None, *, msg=None):
        if multiprocessing.current_process() is self:
            if ret:
                return ret
            else:
                raise RuntimeError(
                    msg or "cant execute operation within self process")


def current_process():
    return multiprocessing.current_process()


get_running_process = current_process
getRunningProcess = current_process
get_current_process = current_process
getCurrentProcess = current_process
