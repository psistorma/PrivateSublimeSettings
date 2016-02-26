import sublime_plugin
from .MUtils import Str

class AutoEscapeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = self.view.sel()

        for region in selections:
            selText = self.view.substr(region)
            selText = selText.replace("\\", "\\\\")
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


        careText = text.strip('_')
        careText.

        isUnderscore = careText
        for srcC in careText:
            if srcC == "_":
                isUnderscore = True
                break

        newText = ""
        if isUnderscore:
            careText.lower()
            needUpper = True
            for idx, srcC in enumerate(careText):
                if srcC == "_":
                    needUpper = True
                    continue

                if needUpper:
                    if idx != 0:
                        srcC = srcC.upper()
                        needUpper = False

                newText += srcC
        else:
            for idx, srcC in enumerate(careText):
                if srcC.isupper():
                    if idx != 0:
                        newText += "_"

                    newText += srcC.lower()
                else:
                    srcC.lower()
                newText += srcC

        return headKeepText + newText + tailKeepText
