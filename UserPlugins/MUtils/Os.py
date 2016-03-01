import subprocess
import os
import sarge
import win32con
from . import Basic

def expandVariable(*strs):
    retStrs = []

    for s in strs:
        retStr = s
        items = os.environ.items()
        for k, v in list(items):
            retStr = retStr.replace('%'+k+'%', v)
        retStrs.append(retStr)

    return tuple(retStrs)

_CMD_MODE_MAP = {
    "run": sarge.run,
    "capture_stdout": sarge.capture_stdout,
    "capture_stderr": sarge.capture_stderr,
    "capture_both": sarge.capture_both,

}
_CMD_KWDS_MAP = {
    "PIPE": subprocess.PIPE,
}

@Basic.fwKeyWordMap(_CMD_KWDS_MAP, ["run_mode", "win_mode"])
def runShellCmd(args, run_mode="capture_both", win_mode="hide", **kwds):
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    runner = _CMD_MODE_MAP[run_mode]
    startupinfo = None
    if win_mode == "hide":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = win32con.SW_HIDE


    out = runner(args, startupinfo=startupinfo, **kwds)
    return (out.returncode,
            out.stdout.text if out.stdout else "!!can't get stdout",
            out.stderr.text if out.stderr else "!!can't get stderr")


