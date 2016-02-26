import subprocess
import os
import shlex
from . import Str


def expandVariable(*strs):
    retStrs = []

    for s in strs:
        retStr = s
        os.path.splitext("C:\\")
        items = os.environ.items()
        for k, v in list(items):
            retStr = retStr.replace('%'+k+'%', v)
        retStrs.append(retStr)

    return retStrs


def runShellCmd(args, opts):
    process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = process.communicate()
    if process.returncode:
        print("The options_script failed with code {0}:".format(process.returncode))
        print(output[1])
        print("****************************************")
    else:
        opts += shlex.split(Str.toUTF8(output[0]))

    return output
