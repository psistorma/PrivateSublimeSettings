import sublime
import os
import json
import collections
from .InvokerLoader import InvokerLoader, Invoker, gInvokerLoader

global gKeyDict

def rease_error(sErr):
  sErr = 'EasyInvoker Err: ' + sErr
  sublime.status_message(sErr)
  raise ValueError(sErr)

class InvokeKeyDict:
  def __init__(self):
    self.refresh()

  def refresh(self):
    self.purge()
    pakDir = sublime.packages_path();
    if not pakDir:
      return

    self.invokeItemsMap = {}
    self.filename = os.path.join(pakDir, 'UserEasyInvoker/easyInvoker.invokeKey.json')
    self.data = open(self.filename, 'r').read()
    self.data = json.loads(self.data, strict=False, object_pairs_hook=collections.OrderedDict)
    self.off = False
    if not self.data:
      self.off = True
      rease_error('easyInvokeKey.json is invalid!')
      return

    for item in self.data['items']:
      self.invokeItemsMap[item['key'].upper()] = item

    sublime.status_message('EasyInvoker refreshed')

  def purge(self):
    self.data = None
    self.invokeItemsMap = None
    gInvokerLoader.unloadAllInvokers()

  def mergeItems(self, mainItems, otherItems):
    reItems = []
    if mainItems is None and otherItems is None:
      return reItems

    if mainItems is None:
      for opt in otherItems:
        if opt.startswith('!'):
          continue
        reItems.append(opt)  
      return reItems

    if otherItems is None:
      for opt in mainItems:
        reItems.append(opt)
      return reItems

    for opt in mainItems:
      if ('!'+opt) in otherItems:
        continue
      reItems.append(opt)

    for opt in otherItems:
      if opt.startswith('!'):
        continue
      if opt not in reItems:
        reItems.append(opt)

    return reItems

  def mergeOpts(self, mainOpts, otherOpts):
    return self.mergeItems(mainOpts, otherOpts)

  def mergeArgs(self, mainArgs, otherArgs):
    return self.mergeItems(mainArgs, otherArgs)

  def regInvokeItem(self, view, destKey, srcKey, opts, args):
    if self.off:
      return

    srcInfo = None
    for info in self.data['invoker_info']:
      if info['key'] == srcKey:
        srcInfo = info
        break

    if srcInfo is None:
      raise ValueError("Can't Find invoker_info for {0}".format(srcKey))

    invoker = srcInfo['invoker']
    expandOpts, expandedArgs = self.prepareOptArg(view, srcInfo['optMap'],
      opts, args, [], [])

    invokeItem = self.queryInvokeItem(destKey)
    if invokeItem is None:
      self.data['items'].append({
        'key': destKey,
        'invoker': invoker,
        'opts': expandOpts,
        'args': expandedArgs
        })
    else:
      invokeItem['invoker'] = invoker
      invokeItem['opts'] = expandOpts
      invokeItem['args'] = expandedArgs

    with open(self.filename, 'w') as outfile:
      json.dump(self.data, outfile, indent=2)

    self.refresh()

  def getDefShort(self):
    return self.data["item_recorder"]["def_short"]

  def getDefLong(self):
    return self.data["item_recorder"]["def_long"]

  def queryInvokeItem(self, invokeKey):
    invokeKeyUpper = invokeKey.upper()
    if invokeKeyUpper not in self.invokeItemsMap:
      return None

    return self.invokeItemsMap[invokeKeyUpper]

  def prepareOptArg(self, view, optMap, mainOpts, mainArgs, otherOpts, otherArgs):
    realMainOpts = []
    realOtherOpts = []
    if mainOpts is not None:
      for opt in mainOpts:
        if optMap is not None:
          realMainOpts.append(optMap[opt])
        else:
          realMainOpts.append(opt)


    if otherOpts is not None:
      for opt in otherOpts:
        if optMap is not None:
          realOtherOpts.append(optMap[opt])
        else:
          realOtherOpts.append(opt)

    opts = self.mergeOpts(realMainOpts, realOtherOpts)
    args = self.mergeArgs(mainArgs, otherArgs)
    
    expandOpts = []
    expandedArgs = []
    for opt in opts:
      expandOpts.append(self.expandAllVariables(view, opt))
    for arg in args:
      expandedArgs.append(self.expandAllVariables(view, arg))

    return (expandOpts, expandedArgs)

  def invokeItemRun(self, view, invokeKey, otherOpts, otherArgs):
    invokeItem = self.queryInvokeItem(invokeKey)
    if invokeItem is None:
      rease_error('invokeKey:' + invokeKey + ' is not exist!')
      return

    expandOpts, expandedArgs = self.prepareOptArg(view, None,
      invokeItem["opts"], invokeItem["args"], otherOpts, otherArgs)

    invoker = gInvokerLoader.mustGetInvoker(invokeItem["invoker"])

    invoker.doWork(view, expandOpts, expandedArgs)

  def expandAllVariables(self, view, val):
    for k, v in list(os.environ.items()):
      val = val.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)


    val = sublime.expand_variables(val, view.window().extract_variables())
    return val

gKeyDict = InvokeKeyDict()
