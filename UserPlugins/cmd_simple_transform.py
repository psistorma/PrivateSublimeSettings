import re
import sublime_plugin
from .MUtils import Str

class ReplaceWithCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwds):
        _from = kwds["from"]
        to = kwds["to"]

        selections = self.view.sel()

        for region in selections:
            selText = self.view.substr(region)
            selText = selText.replace(_from, to)
            self.view.replace(edit, region, selText)

class ToggleCamelUnderscoreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = self.view.sel()

        for region in selections:
            resultText = self.toggleCamelUnderscore(self.view.substr(region))
            self.view.replace(edit, region, resultText)


    @staticmethod
    def toggleCamelUnderscore(text):
        headKeepText = Str.getUtil(text, lambda c: c != "_")
        tailKeepText = Str.getUtil(text, lambda c: c != "_", reverse=True)
        careText = text.strip("_")

        isUnderscore = any(c == "_" for c in careText)

        if isUnderscore:
            newText = re.sub(r"_([a-z])", lambda pat: pat.group(1).upper(), careText)
        else:
            newText = re.sub(r"([A-Z])", lambda pat: "_"+pat.group(1).lower(), careText)
            newText = newText.strip("_")

        return headKeepText + newText + tailKeepText
