import sublime, sublime_plugin

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
      selText = self.view.substr(region)
      headKeepText = ""
      tailKeepText = ""
      for srcC in selText:
        if srcC != "_":
          break
        headKeepText += srcC

      for srcC in selText[::-1]:
        if srcC != "_":
          break
        tailKeepText += srcC

      careText = selText.strip('_')

      isUnderscore = False
      for srcC in careText:
        if srcC == "_":
          isUnderscore = True
          break

      newText = ""
      if isUnderscore:
        print("isUnderscore")
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

      self.view.replace(edit, region, headKeepText + newText + tailKeepText)




