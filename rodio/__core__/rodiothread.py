# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

import threading


class RodioThread(threading.Thread):
    _looper = None

    def __init__(self, target):
        super(RodioThread, self).__init__(target=target)
        self._ended = threading.Event()
        self._started = threading.Event()

    def start(self):
        self._started.set()
        super(RodioThread, self).start()

    def stop(self):
        self._ended.set()

    end = stop
    terminate = stop

    def started(self):
        return self.is_alive() and self._started.is_set()

    has_started = started

    def ended(self):
        return self._ended.is_set()

    has_ended = ended
