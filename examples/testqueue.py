import time
import queue
import threading
import multiprocessing

# Switch from a regular ol' queue to a multiprocess capable one

# queue = queue.Queue()
queue = multiprocessing.Queue()


def target():
    while True:
        print("| wait for content")
        print("|>", queue.get())
        print("| done waiting")


# Switch gears from multiprocessing to multithreading

# threading.Thread(target=target).start()
process = multiprocessing.Process(target=target).start()

while True:
    print("| adding to queue after 3 seconds")
    time.sleep(3)
    queue.put("hey")
    print("| done adding")
