import subprocess
import os
import sarge
import sublime
import win32con

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

def runShellCmd(args, mode="capture_both", hide=True, **kwds):
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    runner = _CMD_MODE_MAP[mode]
    mapKwds = {k: _CMD_KWDS_MAP.get(v, v) for k, v in kwds.items()}
    startupinfo = None
    if hide:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = win32con.SW_SHOWMINIMIZED
    try:
        out = runner(args, startupinfo=startupinfo, **mapKwds)
        return (out.returncode,
                out.stdout.text if out.stdout else "!!can't get stdout",
                out.stderr.text if out.stderr else "!!can't get stderr")
    except Exception as e:
        sublime.error_message(str(e))
        raise e


