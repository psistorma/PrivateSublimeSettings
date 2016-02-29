from collections import namedtuple


def toNamedTuple(dataNameInfo, *data):
    return namedtuple("_", dataNameInfo)(*data)
