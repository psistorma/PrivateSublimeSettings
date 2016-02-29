import functools as ft
from collections import namedtuple
import re
import sublime
import sublime_plugin


def fwNotify(f):
    @ft.wraps(f)
    def wrapper(*args, **kwds):
        result_file_regex = kwds.get("result_file_regex", r'''^\s*File\s*:?\s*"?(.+?)"?,\s*line\s*:?\s*([0-9]+)''')
        replace_regex = kwds.get("replace_regex", (r"\r(?=$)", ""))
        show_result = kwds.get("show_result", "has_output")

        if show_result not in ["allways", "error", "has_output"]:
            raise ValueError("userStorm: value {} of show_result is not support!"
                             .format(show_result))

        errorPanel.result_file_regex = result_file_regex
        errorPanel.replace_regex = replace_regex

        withErr, infos = f(*args, **kwds)
        errorPanel.updateData(infos)

        if show_result == "allways" or (show_result == "error" and withErr):
            errorPanel.show(infos)
        elif show_result == "has_output" and any(info.hasOutput() for info in infos):
            errorPanel.show(errorPanel.formatTolineData(infos))

        if withErr:
            sublime.error_message("meet error!")
        else:
            sublime.status_message("cmd run success")

    return wrapper

class UserstormErrorPanelFlushCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwds):
        data = kwds["data"]
        erase = kwds.get("erase", True)

        if erase:
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, data)

class UserstormErrorPanelHideCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        errorPanel.data = self.view.substr(sublime.Region(0, self.view.size()))

class UserstormErrorPanelShowCommand(sublime_plugin.WindowCommand):
    def run(self, **kwds):
        toggle = kwds.get("toggle", None)
        if toggle:
            if errorPanel.isVisible(self.window):
                errorPanel.close()
            else:
                errorPanel.show(errorPanel.data, self.window)
        else:
            errorPanel.show(errorPanel.data, window=self.window)


class UserStormErrorPanel(object):
    def __init__(self):
        self.view = None
        self.data = None
        self.result_file_regex = ""
        self.replace_regex = ""

    def show(self, data=None, window=None):
        window = window or sublime.active_window()
        if not self.isVisible():
            self.open(window)

        if data is not None:
            self.updateData(data)
            self.flush()

        window.run_command("show_panel", {"panel": "output.userstorm"})


    def updateData(self, data):
        self.data = data

    def get_view(self):
        return self.view

    def isVisible(self, window=None):
        ret = self.view != None and self.view.window() != None
        if ret and window:
            ret = self.view.window().id() == window.id()
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
        errorPanel.view.settings().set("result_file_regex", self.result_file_regex)
        self.view.run_command("userstorm_error_panel_flush", {"data": self.data})

    def open(self, window=None):
        window = window or sublime.active_window()
        if not self.isVisible(window):
            self.view = window.get_output_panel("userstorm")
            errorPanel.view.settings().set("result_file_regex", self.result_file_regex)
            self.view.set_scratch(True)
            fileName = "Packages/UserPlugins/StormErrorPanel.sublime-syntax"
            self.view.set_syntax_file(fileName)
            self.view.set_read_only(False)


    @staticmethod
    def close():
        errorPanel.view.run_command("userstorm_error_panel_hide")
        sublime.active_window().run_command("hide_panel", {"panel": "output.userstorm"})

errorPanel = UserStormErrorPanel()
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

    @classmethod
    def formatSectionLines(cls, sec):
        lines = sec.content.split("\n")
        if errorPanel.replace_regex:
            pat = re.compile(errorPanel.replace_regex[0])
            lines = [pat.sub(errorPanel.replace_regex[1], line) for line in lines]

        return [Info.wrapTitle(sec.title).center(Info.WIDTH, Info.SECTION_FILL_CHAR)] + lines
