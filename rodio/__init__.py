# -*- coding: utf-8 -*-

"""
                            rodio:
Efficient non-blocking event loops for async concurrency and I/O
          Think of this as AsyncIO on steroids
"""

__author__ = "Miraculous Owonubi"
__copyright__ = "Copyright 2019"
__credits__ = ["Miraculous Owonubi"]
__license__ = "Apache-2.0"
__version__ = "0.2.0"
__maintainer__ = "Miraculous Owonubi"
__email__ = "omiraculous@gmail.com"
__status__ = "Development"

from .__core__.eventloop import EventLoop, \
    EventQueue, \
    getRunningLoop, \
    getRunningThread, \
    get_running_loop, \
    get_running_thread


def printprocess(*args, **kwargs):
    thread = getRunningThread()
    print(f'|{thread.name}|> ', *args, **kwargs)
