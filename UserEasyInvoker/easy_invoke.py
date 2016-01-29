import sublime, sublime_plugin
import re
from .InvokeKeyDict import InvokeKeyDict, gKeyDict

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
  def is_visible(self):
    return setting('show_context_menus')

  def run(self):
    self.window.show_input_panel(
      '', '', self.on_done, self.on_change, self.on_cancel)

  def on_done(self, symbol):
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

  def on_change(self, text):
    pass

  def on_cancel(self):
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
