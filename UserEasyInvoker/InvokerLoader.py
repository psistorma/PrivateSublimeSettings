import sublime
import imp
import importlib
import os
import sys
global gInvokerLoader

class InvokerLoader():
  def __init__(self):
    self.invokerMap = {}

  def unloadModule(self, module):
    if "invoker_unloaded" in module.__dict__:
      module.invoker_unloaded()
  
  def loadModule(self, module):
    if "invoker_loaded" in module.__dict__:
      module.invoker_loaded()
  
  def unloadInvoker(self, modulename):
      fullModuleName = __package__ + modulename
      was_loaded = fullModuleName in sys.modules

      if was_loaded:
          m = sys.modules[fullModuleName]
          self.unloadModule(m)
          del sys.modules[fullModuleName]
  
  def reloadInvoker(self, invokeKey):
    print("reloading invoker", invokeKey)
  
    pakDir = sublime.packages_path();
    if not pakDir:
      return

    invokerType = invokeKey + "Invoker"
    modulename = ".invokers." + invokerType
    
    if modulename in sys.modules:
      m = sys.modules[modulename]
      self.unloadModule(m)
      m = imp.reload(m)
    else:
      m = importlib.import_module(modulename, package=__package__)
  
    self.unloadModule(m)
        
    if invokerType not in dir(m):
      raise TypeError("Can't Find Type: {0} in {1}".format(invokerType, modulename))

    t = m.__dict__[invokerType]
    if t.__bases__ and issubclass(t, Invoker):
      self.invokerMap[invokeKey] = {'invoker':t(), 'modulename': modulename}
    else:
      raise TypeError("Type:{0} can be subclass of Invoker!".format(invokerType))
    
  def unloadAllInvokers(self):
    for k, v in self.invokerMap.items():
      self.unloadInvoker(v['modulename'])

    self.invokerMap.clear()
  
  def mustGetInvoker(self, invokeKey):
    if invokeKey not in self.invokerMap:
      self.reloadInvoker(invokeKey)
  
    return self.invokerMap[invokeKey]['invoker']

class Invoker():
  def doWork(self, view, opts, args):
    opts = self.filter_opts(opts)
    args = self.filter_args(args)
    return self.invoke(view, opts, args)

  def parseOpt(self, opt):
    index = opt.find('=')
    if index == -1:
      return {'key': opt, 'val':None }

    return {'key': opt[0, index].upper(), 'val': opt[index + 1:]}

  def filter_opts(self, opts):
    return opts

  def filter_args(self, args):
    return args

  def run(self):
    pass

  def upperItem(self, arr):
    for idx, item in enumerate(arr):
          arr[idx] = item.upper()

gInvokerLoader = InvokerLoader()
