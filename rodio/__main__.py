import sys
from rodio import EventLoop, printfromprocess


def main():
    process = EventLoop(self_pause=False)
    module = process.load_module(sys.argv[1])
    module \
        .on('complete', lambda process: (
            process.scheduleExit() if not process.ended() else None))


if __name__ == "__main__":
    sys.exit(main())
