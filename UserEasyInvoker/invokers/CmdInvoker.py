import sublime
import os
from ..InvokerLoader import Invoker

class CmdInvoker(Invoker):
  def __init__(self):
    pass

  def invoke(self, view, opts, args):
    needWait = False
    needShell = False
    needHide = False
    for opt in opts:
      kv = self.parseOpt(opt)
      if kv['key'].upper() == 'WAIT':
        needWait = True
      if kv['key'].upper() == 'SHELL':
        needShell = True
      if kv['key'].upper() == 'HIDE':
        needHide = True

    import subprocess
    startupinfo = None
    if needHide and os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    command = args
    print(command)
    p = subprocess.Popen(command, startupinfo=startupinfo, shell=needShell)

    if needWait:
      staus = p.wait()
      if staus == 0:
        return
      sublime.error_message("run " + str(command) + "\nWaitAndRetCode: " + str(staus))
    else:
      return
      if p.returncode is None:
        return
      sublime.error_message("run " + str(command) + "\nRetCode: " + str(p.returncode))

