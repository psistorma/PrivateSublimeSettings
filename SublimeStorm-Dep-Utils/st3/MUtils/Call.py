import functools as ft

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

def fwCallBefore(*fnArr):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            for fn in fnArr:
                fn(*args, **kwds)

            return f(*args, **kwds)

        return wrapper

    return decorator
