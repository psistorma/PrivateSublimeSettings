import sublime, sublime_plugin

class PickScopeNameCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    for region in self.view.sel():
      scopeName = self.view.scope_name(region.begin())
      sublime.set_clipboard(scopeName)

  