import functools as ft
from collections import namedtuple
import re
import sublime
import sublime_plugin
from SublimeUtils import Setting

SKEY = "StormOutputView"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

def initSettings():
    defaultOptions = {
        "syntax_file":
        "Packages/SublimeStorm-DPalette/StormOutputView.sublime-syntax",

        "result_file_regex":
        "(?i)^\\s*File\\s*:?\\s*(?:\"|')?(.+?)(?:\"|')?,\\s*line\\s*:?\\s*([0-9]+)",

        "replace_regex":
        {"from": "\\r(?=$)", "to": ""},

        "erase_panel_content": True,

        "scroll_end": True,
    }
    ps.loadWithDefault(defaultOptions)

def fwNotify(f):
    @ft.wraps(f)
    def wrapper(*args, **kwds):
        ret = f(*args, **kwds)
        if ret is None:
            return

        withErr, infos, notifyKwds = ret

        show_result = notifyKwds.get("show_result", "has_output")
        if show_result not in ["allways", "error", "has_output"]:
            raise ValueError("storM: value {} of show_result is not support!"
                             .format(show_result))

        ps.updateDynOpts(**notifyKwds)


        lines = outputView.formatTolineData(infos)
        isInfoShowed = outputView.isVisible()
        if show_result == "allways" or (show_result == "error" and withErr):
            outputView.update(data=lines)
            isInfoShowed = True
        elif show_result == "has_output" and any(info.hasOutput() for info in infos):
            outputView.update(data=lines)
            isInfoShowed = True
        else:
            outputView.update(data=lines, show=False)

        if withErr and not isInfoShowed:
            sublime.error_message("meet error!")
        else:
            sublime.status_message("cmd run success")

    return wrapper

class StormOutputViewFlushCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwds):
        data = kwds["data"]
        erase = kwds.get("erase", True)
        scroll_end = kwds.get("scroll_end", True)

        if erase:
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        elif self.view.size() > 0:
            self.view.insert(edit, self.view.size(), "\n")
        self.view.insert(edit, self.view.size(), data)
        if scroll_end:
            self.view.show(self.view.size())

class StormOutputViewHideCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        outputView.data = self.view.substr(sublime.Region(0, self.view.size()))

class StormOutputViewShowCommand(sublime_plugin.WindowCommand):
    def run(self, **kwds):
        toggle = kwds.get("toggle", None)
        if toggle:
            if outputView.isVisible(self.window):
                outputView.close()
            else:
                outputView.update(data=outputView.data, window=self.window)
        else:
            outputView.update(data=outputView.data, window=self.window)


class StorMOutputView(object):
    def __init__(self):
        self.view = None
        self.data = None

    def update(self, *, data=None, window=None, show=True):
        window = window or sublime.active_window()
        if not self.isVisible(window):
            self.open(window)

        if data is not None:
            self.updateData(data)
            self.flush()

        if show:
            window.run_command("show_panel", {"panel": "output.storm"})


    def updateData(self, data):
        self.data = data

    def get_view(self):
        return self.view

    @staticmethod
    def isVisible(window=None):
        ret = outputView.view != None and outputView.view.window() != None
        if ret and window:
            ret = outputView.view.window().id() == window.id()
        return ret

    @staticmethod
    def formatTolineData(infos):
        lines = []
        for info in infos:
            lines.append(info.formatHeaderLine())
            for sec in info.sections:
                lines.extend(Info.formatSectionLines(sec))

        return "\n".join(lines)

    def flush(self):
        result_file_regex = ps.dynOpts["result_file_regex"]
        if result_file_regex:
            outputView.view.settings().set("result_file_regex", result_file_regex)

        self.view.run_command(
            "storm_error_panel_flush",
            {"data": self.data,
             "erase": ps.dynOpts["erase_panel_content"],
             "scroll_end": ps.dynOpts["scroll_end"],
            })

    def open(self, window=None):
        window = window or sublime.active_window()
        if not self.isVisible(window):
            self.view = window.get_output_panel("storm")
            self.view.settings().set("result_file_regex", ps.dynOpts["result_file_regex"])
            self.view.set_scratch(True)
            fileName = ps.dynOpts["syntax_file"]
            self.view.set_syntax_file(fileName)
            self.view.set_read_only(False)


    @staticmethod
    def close():
        outputView.view.run_command("storm_error_panel_hide")
        sublime.active_window().run_command("hide_panel", {"panel": "output.storm"})

outputView = StorMOutputView()
InfoSection = namedtuple("InfoSection", "title, content, isOutput")
class Info(object):
    def __init__(self, header, *sections):
        self.header = header
        self.sections = [InfoSection._make(sec) for sec in sections]

    WIDTH = 80
    FILL_CHAR = "*"
    SECTION_FILL_CHAR = "-"

    def hasOutput(self):
        return any(sec.content for sec in self.sections if sec.isOutput)

    @classmethod
    def wrapTitle(cls, title):
        return "".join([" = ", title, " = "])

    def formatHeaderLine(self):
        return Info.wrapTitle(self.header).center(Info.WIDTH, Info.FILL_CHAR)

    @staticmethod
    def formatSectionLines(sec):
        lines = sec.content.split("\n")
        replace_regex = ps.dynOpts["replace_regex"]
        if replace_regex:
            pat = re.compile(replace_regex["from"])
            lines = [pat.sub(replace_regex["to"], line) for line in lines]

        return [Info.formatSectionHeader(sec.title)] + lines

    @staticmethod
    def formatSectionHeader(title, landscape=True):
        width = Info.WIDTH if landscape else Info.WIDTH * 9/16
        return Info.wrapTitle(title).center(int(width), Info.SECTION_FILL_CHAR)

def DynamicUpdate(infos, **notifyKwds):
    ps.updateDynOpts(**notifyKwds)
    if "erase_panel_content" not in notifyKwds:
        ps.dynOpts["erase_panel_content"] = False

    if "scroll_end" not in notifyKwds:
        ps.dynOpts["scroll_end"] = False

    lines = outputView.formatTolineData(infos)
    outputView.update(data=lines)
