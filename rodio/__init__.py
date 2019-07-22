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
__version__ = "0.8.0"
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
