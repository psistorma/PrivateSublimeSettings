import shlex
import sublime
import sublime_plugin
from .MUtils import Os
from .SublimeUtils import Setting
from . import ErrorPanel

class PrintSublimeVariableCommand(sublime_plugin.WindowCommand):
    def run(self):
        print(self.window.extract_variables())


class RunShellCmdCommand(sublime_plugin.WindowCommand):
    @ErrorPanel.fwNotify
    def run(self, **kwds):
        commands = kwds["commands"]
        hide = kwds.get("hide", True)
        runOpts = kwds.get("runOpts", {})

        infos = []
        withErr = False
        for cmd in commands:
            cmdArgs = shlex.split(cmd)
            cmdArgs = Setting.expandVariable(self.window, *cmdArgs)

            rc, stdout, stderr = Os.runShellCmd(cmdArgs, hide=hide, **runOpts)
            if not rc:
                withErr = False

            secs = [("command", str(cmdArgs), False)]
            if stderr:
                secs.append(("error info", stderr, True))
            secs.append(("output info", stdout, True))

            infos.append(ErrorPanel.Info("success" if rc else "error", *secs))

        return withErr, infos
