import sarge
from . import Basic

def run(cmd, encoding=None, **kwds):
    ret = sarge.run(cmd, **kwds)
    return Basic.toNamedTuple(
        "returncode, encoding, stdoutText, stderrText",
        ret.returncode,
        encoding,
        ret.stdout.text if ret.stdout else None,
        ret.stderr.text if ret.stderr else None)

def _prepareCapture(encoding, *, wantOut=False, wantErr=False):
    ret = {}
    if wantOut:
        ret["stdout"] = sarge.Capture(encoding=encoding)
    if wantErr:
        ret["stderr"] = sarge.Capture(encoding=encoding)

    return ret

DEFAULT_ENCODINGS = ("UTF-8", "GBK")

@Basic.fwTryDecodings(DEFAULT_ENCODINGS)
def capture_stdout(cmd, encoding, **kwds):
    kwds.update(_prepareCapture(encoding, wantOut=True))
    return run(cmd, encoding, **kwds)

@Basic.fwTryDecodings(DEFAULT_ENCODINGS)
def capture_stderr(cmd, encoding, **kwds):
    kwds.update(_prepareCapture(encoding, wantErr=True))
    return run(cmd, encoding, **kwds)

@Basic.fwTryDecodings(DEFAULT_ENCODINGS)
def capture_both(cmd, encoding, **kwds):
    kwds.update(_prepareCapture(encoding, wantOut=True, wantErr=True))
    return run(cmd, encoding, **kwds)

