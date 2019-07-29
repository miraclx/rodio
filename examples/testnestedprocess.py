import os
import time
import signal
import multiprocessing


def printfromprocess(*args, **kwargs):
    print(multiprocessing.current_process().name, *args, **kwargs)


def child_target():
    printfromprocess("child_process init")
    i = 1
    while i <= 5:
        # Stop iterating after ~ 5 seconds
        time.sleep(2)
        printfromprocess(f"index: {i}, tick after 2 secs")
        if i == 3:
            # Kill the parent process after 3 iterations
            printfromprocess("ending parent process")
            ppid = multiprocessing.current_process()._parent_pid
            os.kill(ppid, signal.SIGTERM)
            printfromprocess("parent process ended")
        i += 1
    printfromprocess("child_process ended")


def main_target():
    printfromprocess("main_process init")
    printfromprocess("Making child process")
    child_process = multiprocessing.Process(
        target=child_target, name="child_process")
    printfromprocess("Starting child process")
    child_process.start()
    printfromprocess("main_process ended")


main_process = multiprocessing.Process(
    target=main_target, name="main_process")

print("root init")
main_process.start()
print("root end")
