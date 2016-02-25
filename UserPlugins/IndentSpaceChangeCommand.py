import sublime
import os
from . import MUtils
import sublime_plugin


class IndentSpaceChangeCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        print(sublime.active_window().extract_variables())
        print("HI")
    # def run(self, edit, **args):
    #     _from = args['from']
    #     to = args['to']
    #     if _from == to:
    #         sublime.error_message("from can't be same as to")
    #         return
    #    self.view.run_command("set_setting",
    #                           {"setting": "tab_size", "value": _from})

    #     self.view.run_command("unexpand_tabs",
    #                           {"set_translate_tabs": True})

    #     self.view.run_command("set_setting",
    #                           {"setting": "tab_size", "value": to})

    #     self.view.run_command("expand_tabs",
    #                           {"set_translate_tabs": True})
