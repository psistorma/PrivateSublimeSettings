import functools as ft

class WrongCallError(Exception):
    def __init__(self, message):
        super().__init__(message)

class TryDecodingError(Exception):
    def __init__(self, hasTryEncodings, *args):
        super().__init__(*args)

        self.hasTryEncodings = hasTryEncodings

    def __str__(self):
        return repr(self.hasTryEncodings)


def fwReportException(reportFun, expType=Exception, reThrow=True):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            try:
                return f(*args, **kwds)
            except expType as e: # pylint: disable=W0703
                reportFun(str(e))
                if reThrow:
                    raise e

        return wrapper

    return decorator
