import time
import threading
import multiprocessing

# Switch from a threading event to a multiprocess capable one

# can_run = threading.Event()
can_run = multiprocessing.Event()


def target():
    while True:
        print("| waiting to run")
        can_run.wait()
        print("| done running")
        can_run.clear()


# Switch gears from multiprocessing to multithreading

# threading.Thread(target=target).start()
process = multiprocessing.Process(target=target).start()

while True:
    print("> setting after 3 seconds")
    time.sleep(3)
    can_run.set()
    print("> done setting")
