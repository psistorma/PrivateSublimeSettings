import re
from collections import namedtuple
import threading
import functools as ft
import dpath.util as du
from jinja2 import Template

def toNamedTuple(dataNameInfo, *data):
    retTuple = namedtuple("retTuple", dataNameInfo)
    if data:
        return retTuple(*data)
    else:
        return retTuple

def _dictMergeWith(dst, src, **kwds):
    du.merge(dst, src, **kwds)
    return dst

def mergeDicts(*dicts, **kwds):
    return ft.reduce(lambda ret, d: _dictMergeWith(ret, d, **kwds), dicts, {})


def promiseInput(pattern, inStr, transTemplate=None, defaultDict=None):
    m = re.match(pattern, inStr)
    if m is None:
        return None

    if transTemplate is None:
        return inStr

    grpDict = {k: v for k, v in m.groupdict().items() if v is not None}
    if defaultDict:
        valDict = mergeDicts(defaultDict, grpDict)
    else:
        valDict = grpDict

    return renderText(transTemplate, **valDict)

def renderText(inStr, **valDict):
    return Template(inStr).render(**valDict)

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
                if reThrow:
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
