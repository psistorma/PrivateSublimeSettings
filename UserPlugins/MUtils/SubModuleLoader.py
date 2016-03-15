import sys
import importlib
from collections import defaultdict

class Loader():
    def __init__(self, moduleType, subModRef, hostPackage):
        self.moduleType = moduleType.lower()
        self.subModRef = subModRef
        self.hostPackage = hostPackage
        self.moduleKeyMap = {}

    def fetchModule(self, moduleKey):
        mod = self.moduleKeyMap.get(moduleKey, None)
        if mod is None:
            mod = self.loadModule(moduleKey)

        return mod

    def moduleName(self, moduleKey):
        return "{0}.{1}".format(self.subModRef, moduleKey)

    def loadModule(self, moduleKey):
        moduleName = self.moduleName(moduleKey)
        if moduleName in sys.modules:
            return Module(moduleKey, sys.modules[moduleName], self)

        m = importlib.import_module(moduleName, package=self.hostPackage)
        return self._regModule(moduleKey, m)

    def unloadModule(self, moduleKey):
        self.moduleKeyMap.pop(moduleKey)
        moduleName = self.moduleName(moduleKey)
        if moduleName not in sys.modules:
            return

        Module(moduleKey, sys.modules[moduleName], self).callIfExist("unloaded")
        del sys.modules[moduleName]

    def reloadModule(self, moduleKey):
        moduleName = self.moduleName(moduleKey)
        if moduleName in sys.modules:
            m = sys.modules[moduleName]
            Module(moduleKey, m, self).callIfExist("unloaded")
            m = importlib.reload(m)
            mod = self._regModule(moduleKey, m)
        else:
            mod = self.loadModule(moduleKey)

        return mod

    def _regModule(self, moduleKey, m):
        mod = Module(moduleKey, m, self)
        mod.callIfExist("loaded")
        self.moduleKeyMap[moduleKey] = mod
        return mod

    def unloadAllModules(self):
        for k in self.moduleKeyMap.keys():
            self.unloadModule(k)


class Module:
    def __init__(self, moduleKey, mod, loader):
        self.moduleKey = moduleKey
        self.mod = mod
        self.loader = loader

    def objByBaseType(self, baseType):
        return self.objDictByBaseType([baseType]).get(baseType, [])

    def objDictByBaseType(self, baseTypes):
        objDict = defaultdict(list)
        for type_name in dir(self.mod):
            try:
                t = self.mod.__dict__[type_name]
                if not t.__bases__:
                    continue

                for baseType in baseTypes:
                    if type_name == baseType.__name__:
                        continue

                    if issubclass(t, baseType):
                        objDict[baseType].append(t)

            except AttributeError:
                pass

        return objDict

    def callIfExist(self, interface, *args, **kwds):
        interface = self._normName(interface)
        if interface in self.mod.__dict__:
            self.mod.__dict__[interface](*args, **kwds)

    def call(self, interface, *args, **kwds):
        interface = self._normName(interface)
        self.mod.__dict__[interface](*args, **kwds)

    def _normName(self, name):
        return "{0}_{1}".format(self.loader.moduleType, name)
