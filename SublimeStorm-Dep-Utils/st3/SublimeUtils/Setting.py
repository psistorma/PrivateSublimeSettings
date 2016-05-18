import copy
import functools as ft
from collections import defaultdict
import dpath.util
import sublime
from MUtils import Os, Str
from . import WView, Selection

_extendVariableKeys = {
    "m_sel_row": lambda vw: str(Selection.getRowCols(vw)[0][0]),
    "m_sel_col": lambda vw: str(Selection.getRowCols(vw)[0][1]),
    "m_sel_text": lambda vw: Selection.getSelTexts(vw)[0],
    "m_sel_lefttext": lambda vw: Selection.getLeftTexts(vw)[0],
    "m_sel_righttext": lambda vw: Selection.getRightTexts(vw)[0],
    "m_sel_line": lambda vw: Selection.getLines(vw)[0],
}
_extendVariableCmds = {
    "!lower": lambda v: v.lower(),
    "!upper": lambda v: v.upper(),
    "!unixpath": lambda v: v.replace("\\", "/"),
    "!020": lambda v: Str.padWithChar(v, "0", 20),
}

@WView.fwPrepareWindow
def expandVariables(window, *strs, forSublime=True, forEnv=True):
    view = window.active_view()
    sublimeVariables = window.extract_variables()

    extendVariables = {k: kFn(view) for k, kFn in _extendVariableKeys.items()}

    for cmd, cmdFn in _extendVariableCmds.items():
        extendVariables.update({
            k+cmd: cmdFn(v) for k, v in sublimeVariables.items()
        })

    sublimeVariables.update(extendVariables)

    retStrs = [sublime.expand_variables(s, sublimeVariables)
               for s in strs] if forSublime else strs
    retStrs = Os.expandVariables(*retStrs) if forEnv else retStrs

    return retStrs

class ProjectSetting():
    def __init__(self, pluginKey):
        self._project_data = sublime.active_window().project_data().get(pluginKey, {}) if int(sublime.version()) >= 3000 else {}

    def get(self, key, default):
        return self._project_data.get(key, default)

    def has(self, key):
        return key in self._project_data

    def items(self):
        return self._project_data.items()

class PluginSetting(object):
    def __init__(self, key, ext='sublime-settings'):
        self.key = key
        self.settingFileName = ".".join([key, ext])
        self.defOpts = None
        self.settings = None
        self.opts = None
        self.dynOpts = None
        self.prevOpts = defaultdict(lambda: None)

    def load(self):
        self.settings = sublime.load_settings(self.settingFileName)
        return self

    def loadWithDefault(self, defOpts, *, onChanged=None, target=None):
        self.load()
        self.defOpts = copy.deepcopy(defOpts)
        self.opts = self.getSetting(target, **self.defOpts)
        self.updateDynOpts()
        def _onChanged():
            nowOpts = self.getSetting(target, **self.defOpts)
            if nowOpts == self.opts:
                return

            self.prevOpts = self.opts
            self.opts = nowOpts
            if onChanged is not None:
                onChanged()

        self.settings.add_on_change(self.key, _onChanged)
        if onChanged is not None:
            onChanged()

    def onPluginUnload(self):
        self.clear_on_change()

    def updateDynOpts(self, **dynKwds):
        projSetting = ProjectSetting(self.key)
        self.dynOpts = {k: projSetting.get(k, v) for k, v in self.opts.items()}
        self.dynOpts = {k: dynKwds.get(k, v) for k, v in self.dynOpts.items()}

    def isValid(self):
        return self.settings is not None

    def clear_on_change(self):
        if self.isValid():
            self.settings.clear_on_change(self.key)

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except KeyError:
            raise AttributeError

    def forTarget(self, target, defVal=None, reLoad=False):
        if reLoad:
            self.load()

        if defVal is None:
            setting = self.settings.get(target)
        else:
            setting = self.settings.get(target, defVal)

        return ft.partial(dpath.util.values, setting)

    def getSetting(self, target=None, expandVarialbe=True, **defaultSettings):
        settings = {}
        if target is None:
            for k, defVal in defaultSettings.items():
                val = self.get(k, defVal)
                if expandVarialbe and isinstance(val, str):
                    settings[k], = expandVariables(None, val)
                else:
                    settings[k] = val
        else:
            _getSetting = self.forTarget(target, {})
            for k, defVal in defaultSettings.items():
                [val] = _getSetting(k) or [defVal]
                if expandVarialbe and isinstance(val, str):
                    settings[k], = expandVariables(None, val)
                else:
                    settings[k] = val

        return settings

def stSettingsFilename():
    if int(sublime.version()) >= 2174:
        return 'Preferences.sublime-settings'
    return 'Global.sublime-settings'




