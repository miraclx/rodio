import sys
from rodio import EventLoop, printfromprocess


def main():
    process = EventLoop(self_pause=False, shared_queue=False)
    module = process.load_module(sys.argv[1], block=True)
    process.terminate()


if __name__ == "__main__":
    sys.exit(main())
