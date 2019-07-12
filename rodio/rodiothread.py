# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import threading
from internals.debug import debug, debugwrapper

__all__ = ['RodioThread',
           'get_running_thread',
           'getRunningThread',
           'get_current_thread',
           'getCurrentThread']


class RodioThread(threading.Thread):
    @debugwrapper
    def __init__(self, target, *, name=None, args=(), kwargs=None, daemon=None, killswitch=None):
        super(RodioThread, self).__init__(target=target,
                                          args=args or (),
                                          kwargs=kwargs or {},
                                          daemon=daemon)

        self.__killswitch = killswitch

        self._ended = threading.Event()
        self.set_name(name or self.name)

    @debugwrapper
    def stop(self):
        if self.ended():
            raise RuntimeError("process already ended")
        if self.__killswitch:
            self.__killswitch()
        self._ended.set()

    end = stop
    terminate = stop

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
        return self.is_alive()

    has_started = started

    def ended(self):
        return self._ended.is_set()

    has_ended = ended


def current_thread():
    return threading.current_thread()


get_running_thread = current_thread
getRunningThread = current_thread
get_current_thread = current_thread
getCurrentThread = current_thread
