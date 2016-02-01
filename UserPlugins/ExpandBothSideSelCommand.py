import sublime, sublime_plugin

class ExpandBothSideSelCommand(sublime_plugin.TextCommand):
  def run(self, edit, count=1):
    selections = self.view.sel()
    newSel = []

    for originalRegion in selections:
      # If point a proceeds point b, reverse it to make calculations easier
      region = originalRegion if originalRegion.a <= originalRegion.b else sublime.Region(originalRegion.b, originalRegion.a)
      print("Info: scope '" + str(self.view.scope_name(region.b -1)) + "', score (" + str(self.view.score_selector(region.a, "string")) + ", " + str(self.view.score_selector((region.b -1), "string")) + ")")

      newRegion = sublime.Region(region.a - count, region.b + count)

      newSel.append(newRegion)

    selections.clear()
    for reg in newSel:
      selections.add(reg)



