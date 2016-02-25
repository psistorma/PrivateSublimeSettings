import sys
import os
import subprocess

def runShellCmd(args, ):
    process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = process.communicate()
    if process.returncode:
        print("The options_script failed with code [%s]" % process.returncode)
        print(output[1])
    else:
        opts += shlex.split(Scommon.bdecode(output[0]))

