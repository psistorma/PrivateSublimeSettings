import os
import json
import tempfile
import sublime_plugin
import sublime
from SublimeUtils import Setting, Project, WView # pylint: disable=F0401
from MUtils.FileDataSrc import JsonAssetSrcManager # pylint: disable=F0401
from SublimeUtils.Context import Context # pylint: disable=F0401
from .panel_asset_base import PanelJsonAssetBaseCommand, AssetType
from .record_base import ProjectWiseJsonAssetRecordBaseCommand

SKEY = "clipboard_palette"
ps = Setting.PluginSetting(SKEY)

class TmpFile:
    def __init__(self):
        self.tmpFile = None
        self.path = "E:\\Tmp2\\test.json"

    def makeTmpFile(self):
        self.purgeFile()
        self.tmpFile = open(self.path, "w")
        self.tmpFile.seek(0)

    def purgeFile(self):
        if self.tmpFile:
            self.tmpFile.close()
            self.tmpFile = None

tmpShowFile = TmpFile()

def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()
    tmpShowFile.purgeFile()

SRC_FILE_EXT = ".clipboard.key"

def initSettings():
    defaultOptions = {
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

        "screen_param": 1300,

        "panel_param": 132,
    }
    ps.loadWithDefault(defaultOptions, onChanged=pwa.onOptionChanged)

quickPanelView = NewGroupPane()

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



pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = ClipboardAssetManager(srcExt=SRC_FILE_EXT, assetKey="assets", key="key")
pwa.ps = ps
pwa.prjInfo = Project.ProjectInfo()


class ClipboardPaletteCommand(PanelJsonAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.curWorkingFile = None
        self.keyIdxLineNumDict = None

    @staticmethod
    def vProjectWiseAssetManager():
        return pwa

    def vEndRun(self, panelData):
        retKeyArr = panelData[1]
        tmpShowFile.makeTmpFile()
        self.keyIdxLineNumDict = {}
        lineNum = 1
        for idx, key in enumerate(retKeyArr):
            assetType, asset = self.assetFromIndex(idx)
            if assetType != AssetType.ASSET_TYPE_CONCRETE:
                continue

            tmpShowFile.tmpFile.write("{}:\n".format(key))
            tmpShowFile.tmpFile.write(asset.val["content"])

            self.keyIdxLineNumDict[idx] = lineNum
            lineNum += 1 + len(asset.val["content"].split("\n"))

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

    @staticmethod
    def getStrFileWithLineNum(filepath, num):
        return "{0}:{1}".format(filepath, num)

    def onQuickPanelHighlight(self, index):
        assetType, asset = self.assetFromIndex(index)
        if assetType == AssetType.ASSET_TYPE_DUMMY:
            return

        lineNum = self.keyIdxLineNumDict[index]

        quickPanelView.openFileTransient(tmpShowFile.path, lineNum)

    def vInvokeAsset(self, asset, assetType):
        quickPanelView.endPane()
        content = asset.val["content"]
        if assetType == AssetType.ASSET_TYPE_CONCRETE:
            sublime.set_clipboard(content)
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






