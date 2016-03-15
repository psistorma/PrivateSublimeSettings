import os
import sublime_plugin
import sublime
from .SublimeUtils import Setting, Panel, WView
from .MUtils import Str, Data
from .MUtils.FileDataSrc import JsonSrcManager
from .SublimeUtils.Context import Context

PROJECT_SRC_BASENAME = ".another_palette"
SRC_FILE_EXT = ".anotherpal.key"

SKEY = "another_palette"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

def initSettings():
    defaultOptions = {
        "palkey_path":
        os.path.dirname(__file__),

        "palkey_path_token":
        "/",

        "project_palkey_path_token":
        ">",

        "dyn_token":
        "//",

        "project_dyn_token":
        ">>",

        "screen_param":
        1300,

        "panel_param":
        132,
    }
    ps.loadWithDefault(defaultOptions, onChanged=updateAssets)

def updateAssets():
    needRebuldAssetKey = True
    curPalkeyPath = ps.opts["palkey_path"]
    if not os.path.exists(curPalkeyPath):
        sublime.error_message("can't visit path: {}!".format(curPalkeyPath))
        srcManager.removeSrc()
        return

    if curPalkeyPath != ps.prevOpts["palkey_path"]:
        srcManager.loadStatic(curPalkeyPath)
        needRebuldAssetKey = False

    srcManager.updateForProjectAssets(sublime.active_window())

    if needRebuldAssetKey:
        srcManager.reBuildAssetKey()

class PalSrcManager(JsonSrcManager):
    def __init__(self, *arg, **kwds):
        super().__init__(*arg, **kwds)

    def reportStatus(self, message):
        print(message)
        sublime.status_message(message)

    def buildAssetKey(self, key, val, srcFile):
        srcDir = srcFile.srcDir
        relPath = os.path.dirname(self.relPath(srcFile, srcDir))

        token = ""
        if srcDir.isStatic:
            if srcFile.isDyn:
                token = ps.opts["dyn_token"]
            else:
                token = ps.opts["palkey_path_token"]
        else:
            if srcFile.isDyn:
                token = ps.opts["project_dyn_token"]
            else:
                token = ps.opts["project_palkey_path_token"]
        tip = val.get("tip", "")
        if tip:
            tip = ps.opts["palkey_path_token"] + tip
        rkey = "".join([token, relPath, tip, "!", key])
        return "\n".join([key, rkey])

    @staticmethod
    def relPath(srcFile, srcDir):
        relPath = os.path.relpath(srcFile.path, srcDir.path)
        relPath = relPath.replace("\\", "/")
        return relPath

    def buildAssetCat(self, asset):
        return self.relPath(asset.srcFile, asset.srcFile.srcDir)

    def updateForProjectAssets(self, window):
        prjAssetPath = self.getProjectAssetPath(window)
        if os.path.exists(prjAssetPath):
            self.switchProject(prjAssetPath)
        else:
            self.projectSrc = None
            self.collectAssets()

    @staticmethod
    def getProjectAssetPath(window):
        project = WView.getProjectPath(window)
        if project is None:
            return None

        workDir, prjFileName = os.path.split(project)
        prjName, _ = os.path.splitext(prjFileName)
        return os.path.join(workDir, PROJECT_SRC_BASENAME, prjName)


srcManager = PalSrcManager(SRC_FILE_EXT)

class AnotherPaletteEventListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        variables = view.window().extract_variables()
        _file = variables['file'].lower()
        if _file.endswith('.anotherpal.key'):
            srcManager.refreshFile(_file)

    def on_load_async(self, view):
        srcManager.updateForProjectAssets(view.window())

class AnotherPaletteCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.globalLastPalKey = None
        self.prjLastPalKeyMap = {}
        self.dummyIndex = -1
        self.indexOfAssetMap = {}

    @Panel.fwShowQuickPanel()
    def run(self):
        view = self.window.active_view()
        selectedIndex = 1
        assets = self.filterByContex(view, srcManager.assets)

        lastPalKey = self.curPrjKeyLastPalKey() or self.globalLastPalKey

        if lastPalKey is not None:
            for idx, asset in enumerate(assets):
                if asset.key == lastPalKey:
                    selectedIndex = idx

        quickInvokeInfoArr = self.alignAssetKey(view, assets)
        self.dummyIndex = -1
        self.dummyIndex = len(quickInvokeInfoArr)
        quickInvokeInfoArr.append(" "*500)

        return self, quickInvokeInfoArr, selectedIndex, sublime.MONOSPACE_FONT

    def curPrjKeyLastPalKey(self):
        return self.prjLastPalKeyMap.get(WView.getProjectPath(self.window), None)

    def regLastPalKey(self, key):
        self.globalLastPalKey = key
        prjPath = WView.getProjectPath(self.window)
        if prjPath is not None:
            self.prjLastPalKeyMap[prjPath] = key


    def filterByContex(self, view, assets):
        filteredAssets = []
        assetKeyIdx = 0
        for idx, asset in enumerate(assets):
            ctx = asset.val.get("context", None)
            if not ctx or Context.check(view, ctx):
                filteredAssets.append(asset)
                self.indexOfAssetMap[assetKeyIdx] = idx
                assetKeyIdx += 1

        return filteredAssets

    @staticmethod
    def alignAssetKey(view, assets):
        ext = view.viewport_extent()
        viewportRate = (ext[0]+30)/(ps.opts["screen_param"])
        panelWidth = int(viewportRate * ps.opts["panel_param"])
        assetKeys = []
        for asset in assets:
            [lhsStr, rhsStr] = asset.key.split("\n")
            assetKeys.append(Str.alignmentBothSide(lhsStr, rhsStr, panelWidth))

        return assetKeys

    def onQuickPanelDone(self, index):
        if index == -1 or index == self.dummyIndex:
            return

        self.invokeAsset(self.indexOfAssetMap[index])

    def invokeAsset(self, index):
        asset = srcManager.asset(index)
        self.regLastPalKey(asset.key)
        command = asset.val["command"]
        args = asset.val.get("args", {})
        cmd_type = asset.val.get("cmd_type", "window")

        if cmd_type == "view":
            self.window.active_view().run_command(command, args)
        elif cmd_type == "window":
            self.window.run_command(command, args)
        elif cmd_type == "app":
            sublime.run_command(command, args)
        else:
            sublime.error_message(
                "{0}'s cmd_type:{1} is not allowed!".format(asset.key, cmd_type))


