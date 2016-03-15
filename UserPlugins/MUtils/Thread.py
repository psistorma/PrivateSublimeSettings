import functools as ft
import threading

def fwRunInThread(f):
    def _f(f, args, kwds):
        f(*args, **kwds)

    @ft.wraps(f)
    def wapper(*args, **kwds):
        threading.Thread(target=_f, args=(f, args, kwds)).start()

    return wapper
