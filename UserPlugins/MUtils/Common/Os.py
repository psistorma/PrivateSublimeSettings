import os

def expandVariable(*strs):
    retStrs = []
    for s in strs:
        retStr = s
        for k, v in list(os.environ.items()):
            retStr = retStr.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)
        retStrs.append(retStr)

    return retStrs
