import re
import fn
import sublime
import sublime_plugin
from .MUtils import Data, Os, Input, Str, Exp, Thread
from .SublimeUtils import Setting, Panel
from . import StormErrorPanel

SKEY = "RunShellCmd"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

def initSettings():
    defaultOptions = {
        "lexical_kwds_modes": [
            #sync and is default
            {"pattern": "(?i)^\\s*@s\\s*(.*)",
             "kwds": {"run_mode": "capture_both",
                      "win_mode": "hide",
                      "async": False},
             "default": True
            },
            #async
            {"pattern": "(?i)^\\s*@a\\s*(.*)",
             "kwds": {"run_mode": "capture_both",
                      "win_mode": "hide",
                      "async": True},
            },
            #show in shell
            {"pattern": "(?i)^\\s*@\\s*(.*)",
             "kwds": {"run_mode": "run",
                      "win_mode": "show",
                      "async": True},
             "transform": "cmd /k {}"
            }
        ]
    }
    ps.loadWithDefault(defaultOptions)

class PrintSublimeVariableCommand(sublime_plugin.WindowCommand):
    def run(self):
        print(self.window.extract_variables())

class RunShellCmdPromptCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.lastInput = ""
        self.cmdKwds = None
        self.lexical_kwds_modes = None

    def run(self, **kwds):
        self.cmdKwds = kwds
        Panel.showInputPanel(self.window, self.onGotInput, "cmd:", self.lastInput)

    def onGotInput(self, content):
        self.lastInput = content
        if not content:
            return

        self.lexical_kwds_modes = ps.opts["lexical_kwds_modes"]
        matched = None
        for mode in self.lexical_kwds_modes:
            m = re.match(mode["pattern"], content)
            if mode.get("default", False):
                matched = mode, m
            if m:
                matched = mode, m
                break

        if matched:
            mode, m = matched

            self.cmdKwds.update(mode["kwds"])
            if m:
                content = m.group(1)

            if "transform" in mode:
                content = mode["transform"].format(content)


        self.cmdKwds["commands"] = content.split(";;")
        self.window.run_command("run_shell_cmd", self.cmdKwds)



ASYNC_STATUS_KEY = "userstorm_async_cmd_status_key"
class RunShellCmdCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.asncCmdCount = 0

    @Input.fwAskQuestions(
        fn.F(Panel.showInputPanel, None),
        fn.F(sublime.error_message, "Canceled on answering question!"))
    def run(self, qAndaDict=None, **kwds):
        sublime.error_message(str(kwds))

        _async = kwds.pop("async", True)
        commands = kwds.pop("commands")
        run_mode = kwds.pop("run_mode", "capture_both")
        win_mode = kwds.pop("win_mode", "hide")
        run_opts = kwds.pop("run_opts", {})
        dyn_report_mul = kwds.pop("dyn_report_mul", True)

        if qAndaDict:
            commands = [Str.renderText(cmd, **qAndaDict) for cmd in commands]

        commands = Setting.expandVariables(self.window, *commands)
        run_opts["cwd"], = Setting.expandVariables(self.window,
                                                   run_opts.get("cwd", "${file_path}"))

        workParams = dict(commands=commands,
                          run_mode=run_mode,
                          win_mode=win_mode,
                          run_opts=run_opts,
                          dyn_report_mul=dyn_report_mul
                         )
        if _async:
            view = self.window.active_view()
            self.asncCmdCount += 1
            if run_mode != "run":
                view.set_status(ASYNC_STATUS_KEY, "***asnc command running***")

            self.doWorkAsnc(view, workParams, **kwds)
        else:
            self.doWork(**Data.mergeDicts(kwds, workParams))


    @Thread.fwRunInThread
    def doWorkAsnc(self, view, workParams, **kwds):
        self.doWork(**Data.mergeDicts(kwds, workParams))
        self.asncCmdCount -= 1
        if self.asncCmdCount == 0:
            view.erase_status(ASYNC_STATUS_KEY)


    @staticmethod
    @StormErrorPanel.fwNotify
    @Exp.fwReportException(sublime.error_message)
    def doWork(commands, run_mode, win_mode, run_opts, dyn_report_mul, **kwds):
        withErr, infos = False, []
        isMulCmd = len(commands) > 1
        for cmd in commands:
            rc, encoding, stdout, stderr = Os.runShellCmd(
                cmd,
                run_mode=run_mode, win_mode=win_mode,
                **run_opts)

            if not rc:
                withErr = False

            if encoding is None:
                secs = [("command", cmd, False)]
            else:
                secs = [("command", "encoding:{0}\n\n{1}".format(encoding, cmd), False)]
            if stderr:
                secs.append(("error/notify", stderr, True))
            secs.append(("output", stdout, True))

            info = StormErrorPanel.Info("success" if rc == 0 else "error", *secs)
            infos.append(info)
            if isMulCmd and dyn_report_mul:
                StormErrorPanel.DynamicUpdate([info], **kwds)

        return (withErr, infos, kwds) if run_mode != "run" else None



