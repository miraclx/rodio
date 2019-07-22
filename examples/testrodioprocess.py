from rodio import RodioProcess, get_current_process


def target(e):
    while e <= 10:
        print('|', get_current_process())
        e += 1


i = 0
while i < 10:
    RodioProcess(target, name=f"process{i}", args=(1,)).start()
    i += 1
