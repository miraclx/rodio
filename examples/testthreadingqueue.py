import threading
from rodio import EventLoop, get_current_thread

process = EventLoop()

process.start()


def queuedFn(name):
    print(f"hello from queued function by {name}")


def queueDecoy():
    thread = get_current_thread()
    print(f"queue from {thread.name}")
    process.nextTick(queuedFn, thread.name)


threads = []
for i in range(10):
    thread = threading.Thread(name=f"thread{i}", target=queueDecoy)
    thread.start()
    threads.append(thread)

[thread.join() for thread in threads]
process.scheduleExit()
