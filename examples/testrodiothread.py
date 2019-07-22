from rodio import RodioThread, get_current_thread


def target(e):
    while e <= 10:
        print('|', get_current_thread())
        e += 1


i = 0
while i < 10:
    RodioThread(target, name=f"process{i}", args=(1,)).start()
    i += 1
