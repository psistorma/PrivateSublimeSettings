import sublime, sublime_plugin

class EnsureInvokeKeyRefreshed(sublime_plugin.EventListener):
  def on_new(self, view):
    view.settings().set("tab_size",2)
    view.settings().set("translate_tabs_to_spaces",True)

  def on_load(self, view):
    view.settings().set("tab_size",2)
    view.settings().set("translate_tabs_to_spaces",True)
    
