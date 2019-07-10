# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import os
import signal
import multiprocessing


class RodioProcess(multiprocessing.context.Process):
    def __init__(self, target, *, name=None, args=(), kwargs=None, daemon=None):
        super(RodioProcess, self).__init__(target=target,
                                           args=args or (),
                                           kwargs=kwargs or {},
                                           daemon=daemon)
        self._started = multiprocessing.Event()
        self._paused = multiprocessing.Event()
        self.set_name(name or self.name)

    def start(self):
        super(RodioProcess, self).start()
        self._started.set()
        self.emit('start')

    def init(self):
        self.start()

    def stop(self):
        # self.__checkNotSelfProcess(msg="cant stop process while within itself")
        if self.ended():
            raise RuntimeError("process already ended")
        if current_process() == self:
            exit()
        else:
            super(RodioProcess, self).terminate()

    def terminate(self):
        self.stop()

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

    def pause(self):
        self.__pause('pause', signal.SIGTSTP)

    def halt(self):
        self.__pause('halt', signal.SIGSTOP)

    def resume(self):
        if not self.has_started():
            raise RuntimeError(
                "unstarted process cant be resumed because it couldn't be paused")
        if self.paused():
            self.__checkNotSelfProcess(
                self, msg="cant pause process while within itself")
            self._paused.clear()
            os.kill(self.pid, signal.SIGCONT)
            self.emit('resume')
        else:
            raise RuntimeError("process not paused")

    def get_pid(self):
        return self.pid

    def getPid(self):
        return self.get_pid()

    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self.name = name

    def setName(self, name):
        self.set_name(name)

    def get_name(self):
        return self.name

    def getName(self):
        return self.get_name()

    def set_daemon(self, state):
        if self.has_started:
            raise RuntimeError(
                "daemonizing process can only be done before initialization of process")
        if not isinstance(state, bool):
            raise TypeError("daemon state must be a boolean datatype")
        self.daemon = state

    def setDaemon(self, state):
        self.set_daemon(state)

    def is_daemon(self):
        return self.daemon

    def isDaemon(self):
        return self.is_daemon()

    def started(self):
        return self._started.is_set()

    def has_started(self):
        return self.started()

    def hasStarted(self):
        return self.started()

    def ended(self):
        return self.has_started and not self.is_alive()

    def has_ended(self):
        return self.ended()

    def hasEnded(self):
        return self.ended()

    def paused(self):
        return self._paused.is_set()

    def has_paused(self):
        return self.paused()

    def hasPaused(self):
        return self.paused()

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
