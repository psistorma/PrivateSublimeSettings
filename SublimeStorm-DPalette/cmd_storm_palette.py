import os
import json
import sublime_plugin
import sublime
from SublimeUtils import Setting, Project # pylint: disable=F0401
from MUtils.FileDataSrc import JsonAssetSrcManager # pylint: disable=F0401
from SublimeUtils.Context import Context # pylint: disable=F0401
from .panel_asset_base import PanelJsonAssetBaseCommand
from .record_base import ProjectWiseJsonAssetRecordBaseCommand

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
        headToken, pathToken = pwa.getAssetHelpInfo(srcFile)
        rkey = "".join([headToken, pathToken])
        return key, rkey

pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = PalAssetManager(srcExt=SRC_FILE_EXT, assetKey="assets", key="key")
pwa.ps = ps
pwa.prjInfo = Project.ProjectInfo()

class StormPaletteCommand(PanelJsonAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def vProjectWiseAssetManager():
        return pwa

    @staticmethod
    def vFormatAssetFileAssetVal(srcFile, key):
        filePath = srcFile.path.replace("\\", "/")
        val = {
            "key": key,
            "command": "eval_python_code",
            "args": {
                "code": "sublime.active_window().open_file(\"{}\")".format(filePath),
                "show_result": "error"
            },
        }
        return val

    def vFilterAsset(self, view, asset):
        ctx = asset.val.get("context", None)

        if pwa.isHidden(asset.key):
            return False

        if ctx and not Context.check(view, ctx):
            return False

        return True

    def vInvokeAsset(self, asset, _):
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

class StormPaletteRecordCommand(ProjectWiseJsonAssetRecordBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def vProjectWiseAssetManager():
        return pwa





