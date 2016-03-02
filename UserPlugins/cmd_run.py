import re
import sublime
import sublime_plugin
from .MUtils import Basic, Os
from .SublimeUtils import Setting, Panel
from . import ErrorPanel

class PrintSublimeVariableCommand(sublime_plugin.WindowCommand):
    def run(self):
        print(self.window.extract_variables())


ASYNC_STATUS_KEY = "userplugin_runcmd_async"
RE_LEXICAL_RUN_MODE_SYNC = r"(?i)^\s*@s\s*(.*)"
RE_LEXICAL_RUN_MODE_ASYNC = r"(?i)^\s*@a\s*(.*)"
RE_LEXICAL_RUN_MODE_SHOW_IN_SHELL = r"(?i)^\s*@\s*(.*)"

class RunShellCmdPropmtCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.lastInput = ""
        self.cmdKwds = None
        self.lexicalKwdsModes = [
            {"pat": re.compile(RE_LEXICAL_RUN_MODE_SYNC),
             "kwds": {"run_mode": "capture_both",
                      "win_mode": "hide",
                      "async": False},
            },
            {"pat": re.compile(RE_LEXICAL_RUN_MODE_ASYNC),
             "kwds": {"run_mode": "capture_both",
                      "win_mode": "hide",
                      "async": True},
            },
            {"pat": re.compile(RE_LEXICAL_RUN_MODE_SHOW_IN_SHELL),
             "kwds": {"run_mode": "run",
                      "win_mode": "show",
                      "async": True},
             "transform": "cmd /k {}"
            },
        ]

    def run(self, **kwds):
        self.cmdKwds = kwds
        Panel.showInputPanel(self.window, self.onGotInput, "cmd:", self.lastInput)

    def onGotInput(self, content):
        self.lastInput = content
        if not content:
            return

        for mode in self.lexicalKwdsModes:
            m = mode["pat"].match(content)
            if m:
                content = m.group(1)
                self.cmdKwds.update(mode["kwds"])
                if "transform" in mode:
                    content = mode["transform"].format(content)
                break

        self.cmdKwds["commands"] = content.split(";;")
        self.window.run_command("run_shell_cmd", self.cmdKwds)

class RunShellCmdCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.asncCmdCount = 0
        self.commands = None
        self.run_mode = None
        self.win_mode = None
        self.run_opts = None

    def run(self, **kwds):
        _async = kwds.pop("async", True)
        self.commands = kwds.pop("commands")
        self.run_mode = kwds.pop("run_mode", "capture_both")
        self.win_mode = kwds.pop("win_mode", "hide")
        self.run_opts = kwds.pop("run_opts", {})
        self.run_opts["cwd"], = Setting.expandVariables(self.window,
                                                        self.run_opts.get("cwd", "${file_path}"))

        if _async:
            view = self.window.active_view()
            self.asncCmdCount += 1
            if self.run_mode != "run":
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
        withErr, infos = False, []
        for cmd in self.commands:
            cmd, = Setting.expandVariables(self.window, cmd)

            rc, encoding, stdout, stderr = Os.runShellCmd(
                cmd,
                run_mode=self.run_mode, win_mode=self.win_mode,
                **self.run_opts)

            if not rc:
                withErr = False

            if encoding is None:
                secs = [("command", cmd, False)]
            else:
                secs = [("command", "encoding:{0}\n\n{1}".format(encoding, cmd), False)]
            if stderr:
                secs.append(("error info", stderr, True))
            secs.append(("output info", stdout, True))

            infos.append(ErrorPanel.Info("success" if rc == 0 else "error", *secs))

        return (withErr, infos, kwds) if self.run_mode != "run" else None



