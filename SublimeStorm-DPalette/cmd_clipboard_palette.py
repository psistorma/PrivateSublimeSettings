import os
import json
import sublime_plugin
import sublime
from MUtils import Os # pylint: disable=F0401
from SublimeUtils import Setting, Project, WView # pylint: disable=F0401
from MUtils.FileDataSrc import JsonAssetSrcManager # pylint: disable=F0401
from SublimeUtils.Context import Context # pylint: disable=F0401
from .panel_asset_base import PanelJsonAssetBaseCommand, AssetType
from .record_base import ProjectWiseJsonAssetRecordBaseCommand
from .StormOutputView import Info

SKEY = "clipboard_palette"
SRC_FILE_EXT = ".clipboard.json"

def plugin_loaded():
    defOpts = defaultOptions()
    pwa.onPluginLoaded(SKEY, defOpts)

def plugin_unloaded():
    pwa.onPluginUnload()



def defaultOptions():
    return {
        #----------------- hidden setting ---------------------
        "project_src_basename": ".clipboard_palette",
        "virtual_asset_token" : "~",
        #----------------- normal setting ---------------------
        "palkey_path":
        os.path.dirname(__file__),

        "palkey_path_token": "/",

        "project_palkey_path_token": ">",

        "dyn_token": "//",

        "project_dyn_token": ">>",

        "panel_width": 45,
    }


class ClipboardPaletteEventListener(sublime_plugin.EventListener):
    @staticmethod
    def on_post_save_async(view):
        pwa.onFileSave(view)

    @staticmethod
    def on_load_async(view):
        pwa.onFileLoad(view)

    @staticmethod
    def on_activated(view):
        quickPanelView.onViewActivated(view)

class ClipboardAssetManager(JsonAssetSrcManager):
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
        if pathToken:
            rkey = "".join([headToken, pathToken])
        else:
            rkey = headToken

        return key, rkey

class ClipboardPaletteCommand(PanelJsonAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.curWorkingFile = None
        self.keyIdxLineNumDict = None
        self.paste = True
        self.needLongPanel = False

    @staticmethod
    def vProjectWiseAssetManager():
        return pwa

    def vBeginRun(self, **kwds):
        self.paste = kwds.get("paste", True)

    def vEndRun(self, panelData):
        if panelData is None:
            return

        retKeyArr = panelData[1]
        tmpShowFile.makeTmpFile(suffix=".stormoutput")
        self.keyIdxLineNumDict = {}
        lineNum = 1
        for idx, key in enumerate(retKeyArr):
            assetType, asset = self.assetFromIndex(idx)
            if assetType != AssetType.ASSET_TYPE_CONCRETE:
                continue

            if idx != 0:
                tmpShowFile.write("\n")
            tmpShowFile.write("{}\n".format(Info.formatSectionHeader(asset.orgKey, False)))
            tmpShowFile.write(asset.val["content"])

            self.keyIdxLineNumDict[idx] = lineNum
            lineNum += 1 + len(asset.val["content"].split("\n"))

        tmpShowFile.close()

        quickPanelView.startPane()
        return panelData

    @staticmethod
    def vPanelFlags():
        return sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST

    @staticmethod
    def vFormatAssetFileAssetVal(srcFile, key):
        val = {
            "key": key,
            "content": srcFile.path,
        }
        return val

    def onQuickPanelHighlight(self, index):
        assetType, asset = self.assetFromIndex(index)
        filePath = None
        lineNum = 0
        if assetType == AssetType.ASSET_TYPE_CONCRETE:
            filePath = tmpShowFile.path
            lineNum = self.keyIdxLineNumDict[index]
        elif assetType == AssetType.ASSET_TYPE_VIRTUAL_FILE:
            filePath = asset.val["content"]
            lineNum = 1
        else:
            return


        quickPanelView.openFileTransient(filePath, lineNum)

    def vInvokeAsset(self, asset, assetType):
        quickPanelView.endPane()
        content = asset.val["content"]
        if assetType == AssetType.ASSET_TYPE_CONCRETE:
            sublime.set_clipboard(content)
            if self.paste:
                self.window.active_view().run_command("paste")
        elif assetType == AssetType.ASSET_TYPE_VIRTUAL_FILE:
            self.window.open_file(content)
        else:
            raise ValueError("assetType: {} is not support!".format(assetType))

    def vOnQuickPanelCancel(self):
        quickPanelView.endPane()


class ClipboardPaletteRecordCommand(ProjectWiseJsonAssetRecordBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def vProjectWiseAssetManager():
        return pwa

    def vPreTransContent(self, _, val):
        if val["content"] == "$<<clipboard>>":
            val["content"] = sublime.get_clipboard()
            return False

        return True

pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = ClipboardAssetManager(srcExt=SRC_FILE_EXT, assetKey="assets", key="key")
pwa.ps = Setting.PluginSetting(SKEY)
pwa.prjInfo = Project.ProjectInfo()

tmpShowFile = Os.TmpFile()
quickPanelView = WView.NewGroupPane("right")




