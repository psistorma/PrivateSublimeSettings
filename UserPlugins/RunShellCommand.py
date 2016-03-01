import shlex
import sublime
import sublime_plugin
from .MUtils import Basic, Os
from .SublimeUtils import Setting
from . import ErrorPanel

class PrintSublimeVariableCommand(sublime_plugin.WindowCommand):
    def run(self):
        print(self.window.extract_variables())


ASYNC_STATUS_KEY = "userplugin_runcmd_async"

class RunShellCmdCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.asncCmdCount = 0

    def run(self, **kwds):
        _async = kwds.pop("async", True)
        if _async:
            view = self.window.active_view()
            self.asncCmdCount += 1
            view.set_status(ASYNC_STATUS_KEY, "***asnc command running***")
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
        commands = kwds.pop("commands")
        run_mode = kwds.pop("run_mode", "capture_both")
        win_mode = kwds.pop("win_mode", "hide")
        run_opts = kwds.pop("run_opts", {})

        withErr, infos = False, []
        for cmd in commands:
            cmdArgs = shlex.split(cmd)
            cmdArgs = Setting.expandVariable(self.window, *cmdArgs)

            rc, stdout, stderr = Os.runShellCmd(
                cmdArgs,
                run_mode=run_mode, win_mode=win_mode,
                **run_opts)

            if not rc:
                withErr = False

            secs = [("command", str(cmdArgs), False)]
            if stderr:
                secs.append(("error info", stderr, True))
            secs.append(("output info", stdout, True))

            infos.append(ErrorPanel.Info("success" if rc else "error", *secs))

        return (withErr, infos, kwds) if run_mode != "run" else None

