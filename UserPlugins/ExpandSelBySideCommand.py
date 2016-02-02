import sublime, sublime_plugin

class ExpandSelBySideCommand(sublime_plugin.TextCommand):
  def run(self, edit, count = 1, side = "both"):
    selections = self.view.sel()
    newSel = []
    for originalRegion in selections:
      # If point a proceeds point b, reverse it to make calculations easier
      region = originalRegion if originalRegion.a <= originalRegion.b else sublime.Region(originalRegion.b, originalRegion.a)

      new_a = region.a
      new_b = region.b
      if side == "both":
        new_a -= count
        new_b += count
      elif side == "left":
        new_a -= count
      elif side == "right":
        new_b += count
      else:
        raise ValueError('side is not valid, must be left,right,both')

      newRegion = sublime.Region(new_a, new_b)

      newSel.append(newRegion)

    selections.clear()
    for reg in newSel:
      selections.add(reg)



