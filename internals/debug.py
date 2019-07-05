def hasArg(arg):
    from sys import argv
    clone = [*argv]
    try:
        clone.remove(arg)
        return True
    except ValueError:
        return False


def debug(fn, *args):
    from datetime import datetime
    if (hasArg('--DEBUG')):
        print(f'[\x1b[33mDEBUG\x1b[0m@\x1b[34m{datetime.now().strftime("%T")}\x1b[0m] [\x1b[32m{fn}\x1b[0m]%s' % (
            f': {", ".join(map(str, args))}' if len(args) else ''))


def debugwrapper(start=1, end=None):
    def wrapper(fn):
        def underlayer(*args, **kwargs):
            debug(f'{fn.__qualname__}() init', *args[start:end])
            fn(*args, **kwargs)
            debug(f'{fn.__qualname__}() exit')
        return underlayer
    if callable(start):
        [start, fn] = [1, start]
        return wrapper(fn)
    return wrapper
