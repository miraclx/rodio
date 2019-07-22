from rodio import EventLoop, get_running_loop, printfromprocess


def function(count):
    count += 1
    printfromprocess(f"function! count -> {count}")
    process = get_running_loop()
    process.nextTick(function, count)


process = EventLoop()
process.nextTick(function, 0)
