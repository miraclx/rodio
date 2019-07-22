import time
import threading
from rodio import EventQueue

queue = EventQueue()

queue.push(lambda: print("hey0"))


def target():
    print("Queue is paused", queue.paused())
    print("Queue has ended", queue.ended())
    time.sleep(2)
    print("Queue is paused", queue.paused())
    print("Queue has ended", queue.ended())
    queue.push(lambda: print("hey1"))
    print("Queue is paused", queue.paused())
    print("Queue has ended", queue.ended())
    queue.end()
    print("Queue is paused", queue.paused())
    print("Queue has ended", queue.ended())


print("init")
threading.Thread(target=target).start()
queue.start()
print("done")
