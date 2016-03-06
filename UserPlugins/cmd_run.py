import re
import fn
import sublime
import sublime_plugin
from .MUtils import Basic, Os
from .SublimeUtils import Setting, Panel
from . import ErrorPanel

pluginSetting = Setting.PluginSetting("UserPlugins")

class PrintSublimeVariableCommand(sublime_plugin.WindowCommand):
    def run(self):
        print(self.window.extract_variables())

SKEY_RUN_SHELL_CMD_PROMPT = "run_shell_cmd_prompt"
class RunShellCmdPromptCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.lastInput = ""
        self.cmdKwds = None
        self.lexical_kwds_modes = None
        self.getSetting = None


    def run(self, **kwds):
        self.getSetting = pluginSetting.forTarget(SKEY_RUN_SHELL_CMD_PROMPT, {})

        self.cmdKwds = kwds
        Panel.showInputPanel(self.window, self.onGotInput, "cmd:", self.lastInput)

    def onGotInput(self, content):
        self.lastInput = content
        if not content:
            return

        [self.lexical_kwds_modes] = self.getSetting("lexical_kwds_modes")
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


def askQuestions(window, onDone, *questions, onChange=None, onCancel=None):
    questions = list(questions)
    if not questions:
        raise ValueError("questions is Empty!")

    qas = {}

    def _askCurQuestion():
        curQuestion = questions.pop()
        key = curQuestion["key"]
        init_text = curQuestion.get("init_text", "")
        title = curQuestion.get("title", key)
        pattern = curQuestion.get("pattern", None)
        answer_tempate = curQuestion.get("answer_tempate", None)
        default_dict = curQuestion.get("default_dict", None)

        def _oneQuestionDone(answer):
            if pattern is not None:
                transAnswer = Basic.promiseInput(pattern, answer, answer_tempate, default_dict)
                if transAnswer is None:
                    tip = "{title}:\n{info}\n{pattern}".format(
                        title=title,
                        info="It is not allowed!\nPlease input angin\nneeded pattern is:",
                        pattern=pattern)
                    Panel.showInputPanel(
                        window, _oneQuestionDone, tip, answer,
                        onChange=onChange, onCancel=onCancel)
                    return
                else:
                    answer = transAnswer

            qas[key] = answer

            if questions:
                _askCurQuestion()
            else:
                onDone(qas)

        Panel.showInputPanel(
            window, _oneQuestionDone, title, init_text,
            onChange=onChange, onCancel=onCancel)


    _askCurQuestion()


ASYNC_STATUS_KEY = "userstorm_async_cmd_status_key"
class RunShellCmdCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.asncCmdCount = 0

    def run(self, **kwds):
        questions = kwds.pop("questions", [])
        if questions:
            askQuestions(self.window, fn.F(self.onFreeQuestion, **kwds), *questions)
        else:
            self.onFreeQuestion(**kwds)

    def onFreeQuestion(self, qAndaDict=None, **kwds):
        _async = kwds.pop("async", True)
        commands = kwds.pop("commands")
        run_mode = kwds.pop("run_mode", "capture_both")
        win_mode = kwds.pop("win_mode", "hide")
        run_opts = kwds.pop("run_opts", {})
        if qAndaDict:
            commands = [Basic.renderText(cmd, **qAndaDict) for cmd in commands]

        commands = Setting.expandVariables(self.window, *commands)
        run_opts["cwd"], = Setting.expandVariables(self.window,
                                                   run_opts.get("cwd", "${file_path}"))

        workParams = dict(commands=commands,
                          run_mode=run_mode,
                          win_mode=win_mode,
                          run_opts=run_opts
                         )
        if _async:
            view = self.window.active_view()
            self.asncCmdCount += 1
            if run_mode != "run":
                view.set_status(ASYNC_STATUS_KEY, "***asnc command running***")

            self.doWorkAsnc(view, workParams, **kwds)
        else:
            self.doWork(**Basic.mergeDicts(kwds, workParams))

    @Basic.fwRunInThread
    def doWorkAsnc(self, view, workParams, **kwds):
        self.doWork(**Basic.mergeDicts(kwds, workParams))
        self.asncCmdCount -= 1
        if self.asncCmdCount == 0:
            view.erase_status(ASYNC_STATUS_KEY)

    @ErrorPanel.fwNotify
    @Basic.fwReportException(sublime.error_message)
    def doWork(self, commands, run_mode, win_mode, run_opts, **kwds):
        withErr, infos = False, []
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
                secs.append(("error info", stderr, True))
            secs.append(("output info", stdout, True))

            infos.append(ErrorPanel.Info("success" if rc == 0 else "error", *secs))

        return (withErr, infos, kwds) if run_mode != "run" else None



