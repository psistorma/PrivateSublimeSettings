from collections import namedtuple
import functools as ft
import threading

def toNamedTuple(dataNameInfo, *data):
    return namedtuple("_", dataNameInfo)(*data)

def fwKeyWordMap(mapping, *ignoreKeys, **defaults):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            mapKwds = {k: mapping.get(v, v)
                       for k, v in kwds.items() if k not in ignoreKeys}
            for k, v in defaults.items():
                mapKwds.setdefault(k, v)

            return f(*args, **mapKwds)

        return wrapper

    return decorator

def fwReportException(reportFun, expType=Exception, reThrow=True):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            try:
                return f(*args, **kwds)
            except expType as e: # pylint: disable=W0703
                reportFun(str(e))
                raise e

        return wrapper

    return decorator


def fwRunInThread(f):
    def _f(f, args, kwds):
        f(*args, **kwds)

    @ft.wraps(f)
    def wapper(*args, **kwds):
        threading.Thread(target=_f, args=(f, args, kwds)).start()

    return wapper


    class TryDecodingError(Exception):
        def __init__(self, hasTryEncodings, *args):
            super().__init__(*args)

            self.hasTryEncodings = hasTryEncodings

        def __str__(self):
            return repr(self.hasTryEncodings)

def fwTryDecodings(defaultEncodings):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            orgDecodeExeption = None
            maybe_encodings = kwds.pop("maybe_encodings", defaultEncodings)
            for encoding in maybe_encodings:
                try:
                    return f(*args, encoding=encoding, **kwds)
                except UnicodeDecodeError as e:
                    orgDecodeExeption = e

            raise TryDecodingError(maybe_encodings, orgDecodeExeption)

        return wrapper

    return decorator
