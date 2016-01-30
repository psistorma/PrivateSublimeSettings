import sublime
import subprocess
import traceback
from ..InvokerLoader import Invoker

class SublimeInvoker(Invoker):
  def __init__(self):
    pass

  def invoke(self, view, opts, args):
    operator = opts[-1]
    obj = "sublime"
    if len(opts) > 1:
      obj = opts[-2]
    if obj.upper() == "WINDOW":
      obj = "view.window()"
    elif obj.upper() == "VIEW":
      obj = "view"

    evalCode = "{0}.{1}".format(obj, operator)
    if len(args) == 0:
      print(evalCode)
      try:
        eval("{0}()".format(evalCode))
        sublime.status_message("Invoke {0}() success".format(evalCode))
      except:
        traceback.print_exc()
        sublime.status_message("Invoke {0}() failed".format(evalCode))

      return

    failCount = sucCount = 0
    for arg in args:
      try:
        arg = arg.replace('\\', '\\\\')
        evalCode = "{0}({1})".format(evalCode, arg)
        print(evalCode)
        eval(evalCode)
        sucCount += 1
      except:
        traceback.print_exc()
        failCount += 1

    if failCount == 0 and sucCount == 0:
      return

    if failCount == 0:
      sublime.status_message("Invoke {0} for {1} success".format(evalCode, str(args)))
      return

    if sucCount == 0:
      sublime.status_message("Invoke {0} for {1} failed".format(evalCode, str(args)))
      return

    sublime.status_message("Invoke failCount:{0}, sucCount:{1} of evalCode:{2} for args:{3}".format(
      failCount, sucCount, evalCode, str(args)))
