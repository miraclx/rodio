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

    def started(self):
        return self.is_alive()

    has_started = started

    def ended(self):
        return self._ended.is_set()

    has_ended = ended
