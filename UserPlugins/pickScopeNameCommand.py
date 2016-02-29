import sublime
import sublime_plugin

class PickScopeNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            scopeName = self.view.scope_name(region.begin())
            self.view.window().show_input_panel(
                'ScopeName', scopeName, self.on_input_panel_done, None, None)

    @staticmethod
    def on_input_panel_done(**args):
        scopeName = args["scopeName"]
        sublime.set_clipboard(scopeName)


