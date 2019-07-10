# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

from threading import Thread, Event, current_thread


class RodioThread(Thread):
    def __init__(self, target, *, name=None, args=(), kwargs=None, daemon=None):
        super(RodioThread, self).__init__(target=target,
                                          args=args or (),
                                          kwargs=kwargs or {},
                                          daemon=daemon)
        self._ended = Event()
        self.set_name(name or self.name)

    def stop(self):
        self._ended.set()

    end = stop
    terminate = stop

    def set_name(self, name):
        if not (name and isinstance(name, str)):
            raise RuntimeError(
                "<name> parameter must be a specified str instance")
        self.name = name

    setName = set_name

    def get_name(self):
        return self.name

    getName = get_name

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
