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
__version__ = "1.0.0"
__maintainer__ = "Miraculous Owonubi"
__email__ = "omiraculous@gmail.com"
__status__ = "Development"

from .eventloop import *
from .eventqueue import *
from .rodiothread import *
from .rodioprocess import *
from .internals.uvloopwrapper import *


def printfromprocess(*args, **kwargs):
    process = get_running_process()
    print(f'|{process.name}|> ', *args, **kwargs)


"""
rodio.EventLoop()
rodio.EventQueue()
rodio.RodioThread()
rodio.RodioProcess()
rodio.get_running_loop()
rodio.get_current_loop()
rodio.check_or_get_loop()
rodio.get_current_thread()
rodio.get_running_thread()
rodio.get_current_process()
rodio.get_running_process()
rodio.is_actively_within_module()

rodio.eventloop
rodio.eventloop.EventLoop()
rodio.eventloop.get_running_loop()
rodio.eventloop.get_current_loop()
rodio.eventloop.check_or_get_loop()
rodio.eventloop.is_actively_within_module()

rodio.eventqueue
rodio.eventqueue.EventQueue()

rodio.rodiothread
rodio.rodiothread.RodioThread()
rodio.rodiothread.get_current_thread()
rodio.rodiothread.get_running_thread()

rodio.rodioprocess
rodio.rodioprocess.RodioProcess()
rodio.rodiothread.get_current_process()
rodio.rodiothread.get_running_process()
"""
