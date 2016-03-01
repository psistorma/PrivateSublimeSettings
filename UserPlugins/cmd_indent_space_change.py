import sublime
import sublime_plugin
from .SublimeUtils import Cmd

class IndentSpaceChangeCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        _from = args['from']
        to = args['to']
        if _from == to:
            sublime.error_message("from can't be same as to")
            return

        Cmd.runCommands(
            self.view,
            ("set_setting", {"setting": "tab_size", "value": _from}),
            ("unexpand_tabs", {"set_translate_tabs": True}),
            ("set_setting", {"setting": "tab_size", "value": to}),
            ("expand_tabs", {"set_translate_tabs": True}))
