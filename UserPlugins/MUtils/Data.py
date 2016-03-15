import json
from collections import namedtuple
import functools as ft
import dpath.util as du

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

def toNormalDict(dictObj):
    return json.loads(json.dumps(dictObj))
