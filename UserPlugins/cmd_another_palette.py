import re
import sublime_plugin
from .SublimeUtils import Setting, Panel

def plugin_loaded():
  gKeyDict.refresh()

def plugin_unloaded():
  gKeyDict.purge()

# class AnotherPaletteEventListener(sublime_plugin.EventListener):
#   def on_post_save(self, view):
#     variables = view.window().extract_variables()
#     _file = variables['file'].lower()
#     if _file.endswith('.anotherpal.key'):
#       gKeyDict.refresh()

class AnotherPaletteCommand(sublime_plugin.WindowCommand):
  def __init__(self, *args):
    super().__init__(*args)
    self.lastPalKey = None
    self.palKeyArr = None

  @Panel.fwShowQuickPanel(onDone)
  def run(self, **kwds):
    selectedIndex = 1
    quickInvokeInfoArr = [1,2,3]


    return quickInvokeInfoArr, selectedIndex

  def onDone(self, index):
    if index == -1:
        return

    print(index)
    return
