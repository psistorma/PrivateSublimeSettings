from os import path, environ
from . import Str

def expandVariable(*strs):
    retStrs = []
    for s in strs:
        retStr = s
        path.splitext("C:\\")
        items = environ.items()
        for k, v in list(items):
            retStr = retStr.replace('%'+k+'%', v)
        retStrs.append(retStr)

    return retStrs

print(Str.StrFun())
input()
