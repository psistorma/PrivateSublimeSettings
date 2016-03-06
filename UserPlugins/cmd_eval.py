import traceback
import sublime
import sublime_plugin
from .MUtils import Basic, Os
from .SublimeUtils import Setting, Panel
from . import ErrorPanel

pluginSetting = Setting.PluginSetting("UserPlugins")

ASYNC_STATUS_KEY = "userstorm_async_code_status_key"
class EvalPythonCodePromptCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.lastInput = ""
        self.cmdKwds = None


    def run(self, **kwds):
        self.cmdKwds = kwds
        Panel.showInputPanel(self.window, self.onGotInput, "python:", self.lastInput)

    def onGotInput(self, content):
        self.lastInput = content
        if not content:
            return

        self.cmdKwds["code"] = content
        self.window.run_command("eval_python_code", self.cmdKwds)

class EvalPythonCodeCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.asncCmdCount = 0
        self.code = None

    def run(self, **kwds):
        _async = kwds.pop("async", True)
        self.code = kwds.pop("code")

        if _async:
            view = self.window.active_view()
            self.asncCmdCount += 1
            view.set_status(ASYNC_STATUS_KEY, "***asnc code running***")

            self.doWorkAsnc(view, **kwds)
        else:
            self.doWork(**kwds)

    @Basic.fwRunInThread
    def doWorkAsnc(self, view, **kwds):
        self.doWork(**kwds)
        self.asncCmdCount -= 1
        if self.asncCmdCount == 0:
            view.erase_status(ASYNC_STATUS_KEY)

    @ErrorPanel.fwNotify
    @Basic.fwReportException(sublime.error_message)
    def doWork(self, **kwds):
        evalCode, = Setting.expandVariables(self.window, self.code)
        err = None
        ret = ""
        try:
            ret = str(eval(evalCode)) # pylint: disable=W0123
        except Exception:   # pylint: disable=W0703
            err = traceback.format_exc()

        secs = [("code", evalCode, False)]
        if err is not None:
            secs.append(("error info", err, True))

        secs.append(("output info", ret, True))
        infos = []
        infos.append(ErrorPanel.Info("success" if err is None else "error", *secs))

        return err is not None, infos, kwds

