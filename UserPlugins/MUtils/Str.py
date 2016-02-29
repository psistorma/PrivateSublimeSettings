
def toUTF8(s):
    return s.encode(encodeing="UTF-8")

def getUtil(s, condifionFun, reverse=False):
    s = s[::-1] if reverse else s
    ret = []
    for c in s:
        if condifionFun(c):
            break
        ret.append(c)

    return ''.join(ret)
