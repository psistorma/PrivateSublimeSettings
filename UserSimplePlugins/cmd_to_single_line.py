import sublime
import sublime_plugin

class ToSingleLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        for region in sels:
            sRegion = self.view.substr(region).replace("\n", "")
            sRegion = sRegion.replace("\r", "")
            self.view.replace(edit, region, sRegion)

