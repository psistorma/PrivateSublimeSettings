import functools as ft
from jinja2 import Template
from . import Exp

def toUTF8(s):
    return s.encode(encodeing="UTF-8")

def alignmentBothSide(lhsStr, rhsStr, width, padChar=" "):
    lhsLen = len(lhsStr)
    rhsLen = len(rhsStr)
    padLen = width - lhsLen - rhsLen
    if padLen < 0:
        return lhsStr + rhsStr

    return lhsStr + padChar*padLen + rhsStr

def renderText(inStr, **valDict):
    return Template(inStr).render(**valDict)

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

            raise Exp.TryDecodingError(maybe_encodings, orgDecodeExeption)

        return wrapper

    return decorator
