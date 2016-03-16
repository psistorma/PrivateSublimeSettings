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

def transfJsonObj(obj, fnNeedTransf, fnTransf):
    return _TransfJsonobj(fnNeedTransf, fnTransf).transf(obj)

class _TransfJsonobj:
    def __init__(self, fnNeedTransf, fnTransf):
        self.fnNeedTransf = fnNeedTransf
        self.fnTransf = fnTransf

    def transf(self, obj):
        if isinstance(obj, dict):
            return self._transfDict(obj)
        elif isinstance(obj, list):
            return self._transfList(obj)
        else:
            return self._transfPrimitive(obj)

    def _transfIt(self, obj, isKey):
        nobj = obj
        if self.fnNeedTransf(obj, isKey):
            nobj = self.fnTransf(obj, isKey)

        return nobj

    def _transfDict(self, obj):
        altered = {}
        for k, v in obj.items():
            nk = self._transfIt(k, True)
            nv = self.transf(v)
            altered[nk] = nv

        return altered

    def _transfList(self, obj):
        altered = []
        for v in obj:
            nv = self.transf(v)
            altered.append(nv)

        return altered

    def _transfPrimitive(self, obj):
        return self._transfIt(obj, False)

