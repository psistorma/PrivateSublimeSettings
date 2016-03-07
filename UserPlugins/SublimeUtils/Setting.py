import functools as ft
from ..MUtils import Os
import sublime
import dpath.util


def expandVariables(window, *strs, forSublime=True, forEnv=True):
    sublimeVariables = window.extract_variables()

    retStrs = [sublime.expand_variables(s, sublimeVariables)
               for s in strs] if forSublime else strs
    retStrs = Os.expandVariables(*retStrs) if forEnv else retStrs

    return retStrs


class PluginSetting(object):
    def __init__(self, baseName, ext='sublime-settings'):
        self.settings = None
        self.settingFileName = ".".join([baseName, ext])

    def load(self):
        self.settings = sublime.load_settings(self.settingFileName)
        return self

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except KeyError:
            raise AttributeError

    def forTarget(self, target, defVal = None, reLoad=True):
        if reLoad:
            self.load()

        if defVal is None:
            setting = self.settings.get(target)
        else:
            setting = self.settings.get(target, defVal)

        return ft.partial(dpath.util.values, setting)

    def getSetting(self, target, **defaultSettings):
        _getSetting = self.forTarget(target, {})
        settings = {}
        for k, defVal in defaultSettings.items():
            [val] = _getSetting(k) or [defVal]
            settings[k] = val

        return settings

