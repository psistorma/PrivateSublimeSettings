import sublime, sublime_plugin
import re
from .InvokeKeyDict import InvokeKeyDict, gKeyDict

VERSION = int(sublime.version())
IS_ST3 = VERSION >=3006

def plugin_loaded():
  gKeyDict.refresh()

def plugin_unloaded():
  gKeyDict.purge()

class EnsureInvokeKeyRefreshed(sublime_plugin.EventListener):
  def on_post_save(self, view):
    variables = view.window().extract_variables()
    file = variables['file'].upper()
    if file.endswith('.INVOKEKEY.JSON') or \
       file.endswith('INVOKER.PY'):
      gKeyDict.refresh()

class EasyInvokeCommand(sublime_plugin.WindowCommand):
  def __init__(self, args):
    sublime_plugin.WindowCommand.__init__(self, args)
    self.lastInvokeKey = None

  def is_visible(self):
    return setting('show_context_menus')

  def run(self):
    self.settings = sublime.load_settings("EasyInvoker.sublime-settings")
    quickList, selectedIndex = self.prepare_quick_panel_list()
    self.show_quick_panel(quickList, self.on_quick_panel_done, selectedIndex)

  def show_quick_panel(self, options, done_callback, index=None):
    if index is None or not IS_ST3:
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done_callback), 10)
    else:
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done_callback, selected_index=index), 10)

  def prepare_quick_panel_list(self):
    selectedIndex = None
    quickInvokeInfoArr = []
    self.quickInvokeKeyArr = []
    for item in gKeyDict.getInvokeItems():
      key = item['key']
      tip = ''
      nPadding = 110 - len(key)
      if 'tip' in item:
        tip = 'tip:  {0}'.format(item['tip'])
        nPadding -= len(tip)

        if nPadding < 0:
          nPadding = 1
        tip = '{{:>{0}}}'.format(nPadding).format(tip)

      if self.lastInvokeKey == key:
        selectedIndex = len(self.quickInvokeKeyArr)
      self.quickInvokeKeyArr.append(key)
      quickInvokeInfoArr.append('{0}{1}'.format(key, tip))

    self.quickInvokeKeyArr.append('>>>>>>>>>>>>Run custom invoke item')
    quickInvokeInfoArr.append('>>>>>>>>>>>>Run custom invoke item')
    self.quickInvokeKeyArr.append('>>>>>>>>>>>>Reg by $as to create invoke item')
    quickInvokeInfoArr.append('>>>>>>>>>>>>Reg by $as to create invoke item')

    return (quickInvokeInfoArr, selectedIndex)

  def on_quick_panel_done(self, index):
    if index == -1:
        return

    symbol = self.quickInvokeKeyArr[index]

    if symbol == '>>>>>>>>>>>>Run custom invoke item':
      self.window.show_input_panel(
        'EasyInvoker', '', self.on_input_panel_done, self.on_input_panel_change, self.on_input_panel_cancel)
      return
    if symbol == '>>>>>>>>>>>>Reg by $as to create invoke item':
      self.window.show_input_panel(
        'EasyInvoker', '$as ', self.on_input_panel_done, self.on_input_panel_change, self.on_input_panel_cancel)
      return

    self.lastInvokeKey = symbol
    self.runInvokeItem(symbol)
    return

  def openFileInCurrentDir(self):
    current = os.path.abspath(self.view.file_name())
    curName = os.path.basename(current)
    path = os.path.dirname(current)
    files = list((file for file in os.listdir(path)
      if os.path.isfile(os.path.join(path, file))))
    if (len(files) > 1):
      targetIndex = files.index(curName) + 1
      if targetIndex >= len(files):
          targetIndex = 0
      target = os.path.join(path, files[targetIndex])
      self.view.window().open_file(target)

  def on_input_panel_done(self, symbol):
    self.runInvokeItem(symbol)

  def runInvokeItem(self, symbol):
    view = self.window.active_view()

    sInfo = symbol.strip(' \t\n\r')
    if not sInfo:
      return

    m = re.search('\s*(?P<s>.*)\s+\$as\s+(?P<d0>.*)|^\$as\s+(?P<d1>.*)', sInfo)
    if m is None:
      self.invoke(view, sInfo)
    else:
      src = m.group('s')
      dest = m.group('d0') or m.group('d1')
      self.define(view, src, dest)

    view.window().focus_view(view.window().active_view())

# def_short
# $as v

# def_long
# c.c.h "start" "" "E:\Code\Web\ReactDev\src\React.js" $as v

# run
# v

  def on_input_panel_change(self, text):
    pass

  def on_input_panel_cancel(self):
    pass

  def invoke(self, view, expression):
    res = self.parseExpression(expression)
    gKeyDict.invokeItemRun(view, res['key'], res['opts'], res['args'])

  def define(self, view, src, dest):
    defineExpression = gKeyDict.getDefShort()
    if src:
      defineExpression = gKeyDict.getDefLong()

    if not defineExpression:
      defineExpression = src

    if not defineExpression:
      raise ValueError('defineExpression is empty')

    if src is not None:
      srcPInfo = src.split('$p')
      srcNInfo = src.split()

      for idx, srcP in enumerate(srcPInfo):
        defineExpression = defineExpression.replace('$p'+str(idx), srcP)

      for idx, srcN in enumerate(srcNInfo):
        defineExpression = defineExpression.replace('$'+str(idx+1), srcN)

      defineExpression = defineExpression.replace('$$', src)

    res = self.parseExpression(defineExpression)

    gKeyDict.regInvokeItem(view, dest, res['key'], res['opts'], res['args'])

  def parseExpression(self, expression):
    m = re.search('\s*(?P<k>[^\s\.]+)(?P<o>\\.?[^\s]*)\s*(?P<a>.*)', expression)

    if m is None:
      raise ValueError('expression is invalid')

    res = {'key': m.group('k'), 'opts': m.group('o'), 'args': m.group('a')}

    if res['opts']:
      res['opts'] = res['opts'].strip('.')
      res['opts'] = res['opts'].split('.')
      for idx, opt in enumerate(res['opts']):
        res['opts'][idx] = opt.strip(' \t\n\r')
    else:
      res['opts'] = None

    if res['args']:
      res['args'] = res['args'].split()
      for idx, arg in enumerate(res['args']):
        res['args'][idx] = arg.replace('$_', '')
    else:
      res['args'] = None

    return res
