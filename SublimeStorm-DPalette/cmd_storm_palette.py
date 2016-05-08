import os
import json
import sublime_plugin
import sublime
from SublimeUtils import Setting, Project # pylint: disable=F0401
from MUtils.FileDataSrc import JsonAssetSrcManager, Asset # pylint: disable=F0401
from SublimeUtils.Context import Context # pylint: disable=F0401
from .panel_asset_base import PanelAssetBaseCommand
from .record_base import RecordJsonAssetBaseCommand

SKEY = "storm_palette"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

SRC_FILE_EXT = ".stormpal.key"

def initSettings():
    defaultOptions = {
        #----------------- hidden setting ---------------------
        "project_src_basename": ".storm_palette",
        "virtual_asset_token" : "~",
        #----------------- normal setting ---------------------
        "palkey_path":
        os.path.dirname(__file__),

        "palkey_path_token": "/",

        "project_palkey_path_token": ">",

        "dyn_token": "//",

        "project_dyn_token": ">>",

        "screen_param": 1300,

        "panel_param": 132,
    }
    ps.loadWithDefault(defaultOptions, onChanged=pwa.onOptionChanged)

class StormPaletteEventListener(sublime_plugin.EventListener):
    @staticmethod
    def on_post_save_async(view):
        pwa.onFileSave(view)

    @staticmethod
    def on_load_async(view):
        pwa.onFileLoad(view)

class PalAssetManager(JsonAssetSrcManager):
    def __init__(self, *arg, **kwds):
        super().__init__(*arg, **kwds)

    @staticmethod
    def vReportStatus(message):
        print(message)
        sublime.status_message(message)

    @staticmethod
    def vIsDynFile(srcFilePath):
        return pwa.isDynFile(srcFilePath)

    @staticmethod
    def vBuildAssetKey(key, val, srcFile):
        headToken, pathToken, tip = pwa.getAssetHelpInfo(srcFile, val.get("tip", ""))
        rkey = "".join([headToken, pathToken, tip, "!", key])
        return "\n".join([key, rkey])

pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = PalAssetManager(srcExt=SRC_FILE_EXT, assetKey="assets", key="key")
pwa.ps = ps
pwa.prjInfo = Project.ProjectInfo()

class StormPaletteCommand(PanelAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vOpts(self, optKey):
        return pwa.opts(optKey)

    def vPrjInfo(self):
        return pwa.prjInfo

    def vAssets(self):
        assets = pwa.am.assets[::]
        self.virutalAssets = self.makeVirtualAssets()
        assets.extend(self.virutalAssets)
        for asset in assets:
            asset.key = asset.key.lower()

        return assets

    @staticmethod
    def vConcreteAssets():
        return pwa.am.assets

    @staticmethod
    def vMakeAssetFileAsset():
        assetFileAssets = []
        for srcFile in pwa.am.srcFiles:
            pathToken = pwa.assetPathToken(srcFile)
            cat = "key.dyn" if srcFile.isDyn else "key"
            virtualAssetToken = pwa.opts("virtual_asset_token")
            key = "".join([virtualAssetToken, cat, virtualAssetToken, pathToken])
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
            assetKey = pwa.am.vBuildAssetKey(key, val, srcFile)
            assetFileAssets.append(Asset(assetKey, assetKey, val, srcFile))

        return assetFileAssets

    def vFilterAsset(self, view, asset):
        ctx = asset.val.get("context", None)

        if pwa.isHidden(asset.key):
            return False

        if ctx and not Context.check(view, ctx):
            return False

        return True

    def vInvokeAsset(self, asset):
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

class StormPaletteRecordCommand(RecordJsonAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vGetRecordFilePath(self, belong_to_project):
        if belong_to_project:
            assetDirectory = pwa.getProjectAssetDirectory(self.window, True)
        else:
            assetDirectory = pwa.getStaticAssetDirectory()

        return pwa.getDynAssetFilePath(assetDirectory)

    def vSaveRecordFile(self, recordFilePath, contentDict, belong_to_project):
        isFileExist = os.path.exists(recordFilePath)

        with open(recordFilePath, "w") as f:
            json.dump(contentDict, f, indent=4)

        if isFileExist:
            pwa.am.refreshFile(recordFilePath)
        else:
            if belong_to_project:
                pwa.am.refreshProjectAssets(self.window)
            else:
                pwa.am.loadStatic(recordFilePath)






