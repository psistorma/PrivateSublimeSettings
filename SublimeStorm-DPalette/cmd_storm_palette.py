import os
import json
import fn
import sublime_plugin
import sublime
from SublimeUtils import Setting, Panel, WView, Project
from MUtils import Os, Str, Data, Input, Exp
from MUtils.FileDataSrc import JsonSrcManager, Asset
from SublimeUtils.Context import Context

PROJECT_SRC_BASENAME = ".storm_palette"
SRC_FILE_EXT = ".stormpal.key"
DYN_SRC_FILENAME = "default.dyn.stormpal.key"
VIRTUAL_ASSET_TOKEN = "~"
HIDDEN_ASSET_TOKEN = "hidden-"

SKEY = "storm_palette"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

def initSettings():
    defaultOptions = {
        "palkey_path":
        os.path.dirname(__file__),

        "palkey_path_token": "/",

        "project_palkey_path_token": ">",

        "dyn_token": "//",

        "project_dyn_token": ">>",

        "screen_param": 1300,

        "panel_param": 132,
    }
    ps.loadWithDefault(defaultOptions, onChanged=updateAssets)

def updateAssets():
    needRebuldAssetKey = True
    curPalkeyPath = ps.opts["palkey_path"]
    if not os.path.exists(curPalkeyPath):
        sublime.error_message("can't visit path: {}!".format(curPalkeyPath))
        Pm.removeSrc()
        return

    if curPalkeyPath != ps.prevOpts["palkey_path"]:
        Pm.loadStatic(curPalkeyPath)
        needRebuldAssetKey = False

    Pm.updateForProjectAssets(sublime.active_window())

    if needRebuldAssetKey:
        Pm.reBuildAssetKey()

class StormPaletteEventListener(sublime_plugin.EventListener):
    @staticmethod
    def on_post_save_async(view):
        variables = view.window().extract_variables()
        _file = variables['file'].lower()
        if _file.endswith('.stormpal.key'):
            Pm.refreshFile(_file)

    @staticmethod
    def on_load_async(view):
        Pm.updateForProjectAssets(view.window())

class PalKeySrcManager(JsonSrcManager):
    def __init__(self, *arg, **kwds):
        super().__init__(*arg, **kwds)

    def reportStatus(self, message):
        print(message)
        sublime.status_message(message)

    @staticmethod
    def isDynFile(srcFilePath):
        return os.path.basename(srcFilePath).lower() == DYN_SRC_FILENAME

    @staticmethod
    def buildAssetKey(key, val, srcFile):
        return Pm.makeAssetKey(key, val.get("tip", ""), srcFile)

    @staticmethod
    def pathToken(srcFile):
        if Pm.isDynFile(srcFile.path):
            return ""

        relPath = os.path.relpath(srcFile.path, srcFile.srcDir.path)
        relPath = relPath.replace("\\", "/")
        return os.path.dirname(relPath)

    @staticmethod
    def makeAssetKey(key, tip, srcFile):
        pathToken = Pm.pathToken(srcFile)

        headToken, tipToken = "", ""
        if srcFile.srcDir.isStatic:
            if srcFile.isDyn:
                headToken = ps.opts["dyn_token"]
            else:
                headToken = ps.opts["palkey_path_token"]
        else:
            if srcFile.isDyn:
                headToken = ps.opts["project_dyn_token"]
            else:
                headToken = ps.opts["project_palkey_path_token"]

        tipToken = ps.opts["palkey_path_token"]

        if tip and pathToken:
            tip = tipToken + tip

        rkey = "".join([headToken, pathToken, tip, "!", key])
        return "\n".join([key, rkey])

    def updateForProjectAssets(self, window):
        prjAssetPath = self.getProjectAssetPath(window)
        if os.path.exists(prjAssetPath):
            self.switchProject(prjAssetPath)
        else:
            self.projectSrc = None
            self.collectAssets()

    @staticmethod
    def getProjectAssetPath(window, makeIfNotExist=False):
        project = WView.getProjectPath(window)
        if project is None:
            return None

        workDir, prjFileName = os.path.split(project)
        prjName, _ = os.path.splitext(prjFileName)
        assetPath = os.path.join(workDir, PROJECT_SRC_BASENAME, prjName)
        if makeIfNotExist and os.path.exists(assetPath):
            os.mkdir(assetPath)

        return assetPath

    @staticmethod
    def getStaticAssetPath():
        return ps.opts["palkey_path"]

    @staticmethod
    def getDynAssetFile(assetPath):
        return os.path.join(assetPath, DYN_SRC_FILENAME)

    @staticmethod
    def isHidden(key):
        return key.lower().startswith(HIDDEN_ASSET_TOKEN)

Pm = PalKeySrcManager(SRC_FILE_EXT)

class StormPaletteCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.prjInfo = Project.ProjectInfoManager()
        self.dummyIndex = -1
        self.indexOfAssetMap = {}
        self.virutalAssets = None

    @Panel.fwShowQuickPanel()
    def run(self, **kwds):
        key = kwds.get("key", None)
        iter_key_head = kwds.get("iter_key_head", None)
        iter_next = kwds.get("iter_next", True)
        title = kwds.get("title", None)

        if key is not None:
            self.invokeKey(key)
            return

        if iter_key_head is not None:
            self.iterKey(title, iter_key_head, iter_next)
            return

        view = self.window.active_view()
        selectedIndex = 1
        assets = self.filterAssets(view, self.assets())

        lastPalKey = self.prjInfo.tVal("last_palkey")
        if lastPalKey is not None:
            for idx, asset in enumerate(assets):
                if asset.key == lastPalKey:
                    selectedIndex = idx

        quickInvokeInfoArr = self.alignAssetKey(view, assets)
        self.dummyIndex = -1
        self.dummyIndex = len(quickInvokeInfoArr)
        quickInvokeInfoArr.append(" "*500)

        return self, quickInvokeInfoArr, selectedIndex, sublime.MONOSPACE_FONT

    @staticmethod
    def makeReadableTitle(title, candidate):
        if title is not None:
            return title

        candidate.lstrip(HIDDEN_ASSET_TOKEN)
        return Str.readableInfo(candidate)

    def assets(self):
        assets = Pm.assets[::]
        self.virutalAssets = self.makeVirtualAssets()
        assets.extend(self.virutalAssets)
        for asset in assets:
            asset.key = asset.key.lower()

        return assets

    def makeVirtualAssets(self):
        virutalAssets = []
        virutalAssets.extend(self.makeAssetFileAsset())
        return virutalAssets

    @staticmethod
    def makeAssetFileAsset():
        assetFileAssets = []
        for srcFile in Pm.srcFiles:
            pathToken = Pm.pathToken(srcFile)
            cat = "key.dyn" if srcFile.isDyn else "key"
            key = "".join([VIRTUAL_ASSET_TOKEN, cat, VIRTUAL_ASSET_TOKEN, pathToken])
            key = key.rstrip(".")
            key = "{0}({1})".format(key, len(srcFile.assets))
            tip = "storm_palette/"+cat
            filePath = srcFile.path.replace("\\", "/")
            val = {
                "command": "eval_python_code",
                "key": key,
                "args": {
                    "code": "sublime.active_window().open_file(\"{}\")".format(filePath),
                    "show_result": "error"
                },
                "tip": tip
            }
            assetKey = Pm.buildAssetKey(key, val, srcFile)
            assetFileAssets.append(Asset(assetKey, assetKey, val, srcFile))

        return assetFileAssets

    def filterAssets(self, view, assets):
        filteredAssets = []
        assetKeyIdx = 0
        for idx, asset in enumerate(assets):
            ctx = asset.val.get("context", None)

            if Pm.isHidden(asset.key):
                continue

            if ctx and not Context.check(view, ctx):
                continue

            filteredAssets.append(asset)
            self.indexOfAssetMap[assetKeyIdx] = idx
            assetKeyIdx += 1

        return filteredAssets

    @staticmethod
    def getLineNumerExt(view):
        lineCount = view.rowcol(view.size())[0] + 1
        return len(str(lineCount)) * 8.5

    @staticmethod
    def alignAssetKey(view, assets):
        ext = view.viewport_extent()
        viewportRate = (ext[0]+StormPaletteCommand.getLineNumerExt(view))/(ps.opts["screen_param"])
        panelWidth = int(viewportRate * ps.opts["panel_param"])
        assetKeys = []
        for asset in assets:
            [lkey, rkey] = asset.key.split("\n")
            assetKeys.append(Str.alignmentBothSide(lkey, rkey, panelWidth))

        return assetKeys

    def onQuickPanelDone(self, index):
        if index == -1 or index == self.dummyIndex:
            return

        index = self.indexOfAssetMap[index]
        vitualIndex = index - len(Pm.assets)
        if vitualIndex >= 0:
            self.invokeAsset(self.virutalAssets[vitualIndex], True)
        else:
            self.invokeAsset(Pm.asset(index), True)

    def invokeKey(self, key):
        key = key.lower()
        for asset in self.assets():
            if asset.key == key:
                self.invokeAsset(asset)
                return

    def invokeAsset(self, asset, regAsLastKey=False):
        if regAsLastKey:
            self.prjInfo.regItem("last_palkey", asset.key)

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

    def iterKey(self, title, keyHead, iterNext):
        title = self.makeReadableTitle(title, keyHead)
        assets = []
        for asset in self.assets():
            if asset.key.startswith(keyHead):
                assets.append(asset)

        if len(assets) == 0:
            sublime.message_dialog("{} is not exist".format(title))
            return

        curIndex = 0

        lastIterKey = self.prjInfo.val("last_iterkey")
        if lastIterKey is not None:
            for idx, asset in enumerate(assets):
                if asset.key == lastIterKey:
                    curIndex = (idx + 1) if iterNext else (idx - 1)

        curIndex = curIndex % len(asset)
        asset = assets[curIndex]
        self.invokeAsset(asset)
        self.prjInfo.regItem("last_iterkey", asset.key, False)

class StormPaletteRecordCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.transfKey = None
        self.transfVal = None
        self.qAndaDict = None
        self.need_expand_variables = None

    @Input.fwAskQuestions(
        fn.F(Panel.showInputPanel, None),
        fn.F(sublime.message_dialog, "Canceled on answering question!"))
    @Exp.fwReportException(sublime.error_message)
    def run(self, qAndaDict=None, **kwds):
        content = kwds.get("content")
        ignore_target = kwds.get("ignore_target", [])
        self.transfKey = "key" not in ignore_target
        self.transfVal = "val" not in ignore_target
        self.need_expand_variables = kwds.get("need_expand_variables", True)
        belong_to_project = kwds.get("belong_to_project", False)
        record_mode = kwds.get("record_mode", "record")
        self.qAndaDict = qAndaDict

        key = content["key"]
        if self.qAndaDict is not None:
            key = Str.renderText(key, **self.qAndaDict)

        key = key.lower()
        if record_mode == "erase":
            self.eraseRecord(key, belong_to_project)
            return
        elif record_mode == "toggle":
            self.eraseRecord(key, belong_to_project)
        elif record_mode == "record":
            pass
        else:
            sublime.error_message("record_mode: {} is not allowed".format(record_mode))

        content = Data.transfJsonObj(content, self.needTransf, self.transf)
        self.recordContent(key, content, belong_to_project)

    def needTransf(self, obj, isKey):
        if isKey and not self.transfKey:
            return False

        if not isKey and not self.transfVal:
            return False

        return isinstance(obj, str)

    def transf(self, obj, _):
        if self.qAndaDict is not None:
            obj = Str.renderText(obj, **self.qAndaDict)

        if self.need_expand_variables:
            obj, = Setting.expandVariables(self.window, obj)

        return obj

    def getDynFile(self, belong_to_project):
        if belong_to_project:
            assetPath = Pm.getProjectAssetPath(self.window, True)
        else:
            assetPath = Pm.getStaticAssetPath()

        dynFilePath = Pm.getDynAssetFile(assetPath)

        return dynFilePath, os.path.exists(dynFilePath)

    @staticmethod
    def eraseAsset(dynFileDict, key):
        filtered = [asset for asset in dynFileDict["assets"] if asset["key"].lower() != key]
        if len(filtered) != len(dynFileDict["assets"]):
            dynFileDict["assets"] = filtered
            return True

        return False

    def dumpDynFile(self, dynFilePath, dynFileDict, belong_to_project):
        isFileExist = os.path.exists(dynFilePath)
        if belong_to_project and not isFileExist:
            Os.promiseDirectory(os.path.dirname(dynFilePath))

        with open(dynFilePath, "w") as f:
            json.dump(dynFileDict, f, indent=4)

        if isFileExist:
            Pm.refreshFile(dynFilePath)
        else:
            if belong_to_project:
                Pm.updateForProjectAssets(self.window)
            else:
                Pm.loadStatic(dynFilePath)

    def eraseRecord(self, key, belong_to_project):
        dynFilePath, isFileExist = self.getDynFile(belong_to_project)
        if not isFileExist:
            return

        with open(dynFilePath, "r") as f:
            dynFileDict = json.load(f)

        if not self.eraseAsset(dynFileDict, key):
            return

        self.dumpDynFile(dynFilePath, dynFileDict, belong_to_project)

    def recordContent(self, key, content, belong_to_project):
        dynFilePath, isFileExist = self.getDynFile(belong_to_project)
        if isFileExist:
            with open(dynFilePath, "r") as f:
                dynFileDict = json.load(f)

            self.eraseAsset(dynFileDict, key)
        else:
            dynFileDict = {"assets": []}

        dynFileDict["assets"].append(content)
        self.dumpDynFile(dynFilePath, dynFileDict, belong_to_project)






