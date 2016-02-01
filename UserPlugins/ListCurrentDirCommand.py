import sublime
import sublime_plugin
import os
import errno
import re

VERSION = int(sublime.version())
IS_ST3 = VERSION >=3006
CUR_ITER_ORDER = 1

def _ignore_file(filename, ignore_patterns=[]):
    ignore = False
    directory, base = os.path.split(filename)
    for pattern in ignore_patterns:
        if re.match(pattern, base):
            return True

    if len(directory) > 0:
        ignore = _ignore_file(directory, ignore_patterns)

    return ignore

def _list_path_file(path, ignore_patterns=[]):
   file_list = []
   if not os.path.exists(path):
      sMsg = "{0} is not exist or can't visited!".format(path)
      sublime.error_message(sMsg)
      raise ValueError(sMsg)

   for file in os.listdir(path):
      if not _ignore_file(file, ignore_patterns):
        file_list.append(file)

   return sorted(file_list)

class ListCurrentDirCommand(sublime_plugin.TextCommand):
  def __init__(self, args):
    sublime_plugin.TextCommand.__init__(self, args)

  def run(self, edit):
    self.settings = sublime.load_settings("ListCurrentDir.sublime-settings")
    current = os.path.abspath(self.view.file_name())
    self.curName = os.path.basename(current)

    self.ignore_patterns = self.settings.get("ignore_patterns", ['.*?\.tags'])
    self.show_dir_file(os.path.dirname(current))

  def show_dir_file(self, path):
    self.path = path
    self.build_quick_panel_file_list()

    index = self.quick_panel_files.index(self.curName) + CUR_ITER_ORDER
    if index >= len(self.quick_panel_files) or index <= 1:
      if CUR_ITER_ORDER == 1:
        index = 2
      else:
        index = len(self.quick_panel_files) - 1

    self.show_quick_panel(self.quick_panel_files, self.path_file_callback, index)

  def build_quick_panel_file_list(self):
    self.path_objs = {}
    self.quick_panel_files = []
    if CUR_ITER_ORDER == 1:
      self.quick_panel_files.append("/* change iter order to prev */")
    else:
      self.quick_panel_files.append("/* change iter order to next */")

    if os.path.exists(os.path.dirname(os.path.dirname(self.path))):
      self.quick_panel_files.append("..")

    files_list = _list_path_file(self.path, self.ignore_patterns)
    dirs = []
    files = []
    for file in files_list:
      if os.path.isfile(os.path.join(self.path, file)):
        files.append(file)
      else:
        dirs.append(file + '/')

    self.quick_panel_files += dirs
    self.quick_panel_files += files

  def is_file(self, entry):
    return not entry.endswith('/')

  def path_file_callback(self, index):
    global CUR_ITER_ORDER
    if index == -1:
      return

    entry = self.quick_panel_files[index]

    if entry == "..":
      self.show_dir_file(os.path.dirname(os.path.dirname(self.path)))
      return
    elif entry == "/* change iter order to prev */":
      CUR_ITER_ORDER = -1
      return
    elif entry == "/* change iter order to next */":
      CUR_ITER_ORDER = 1
      return
    else:
      target = os.path.join(self.path, entry)
      if self.is_file(entry):
        self.view.window().open_file(target)
      else:
        self.show_dir_file(target)

  def show_quick_panel(self, options, done_callback, index=None):
    if index is None or not IS_ST3:
      sublime.set_timeout(lambda: self.view.window().show_quick_panel(options, done_callback), 10)
    else:
      sublime.set_timeout(lambda: self.view.window().show_quick_panel(options, done_callback, selected_index=index), 10)
