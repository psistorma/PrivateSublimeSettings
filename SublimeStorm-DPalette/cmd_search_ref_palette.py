import os
import sublime_plugin
import sublime
from SublimeUtils import Setting, Project # pylint: disable=F0401
from MUtils import MarkDownInfo # pylint: disable=F0401
from MUtils.FileDataSrc import AssetSrcManager, Asset # pylint: disable=F0401
from .panel_asset_base import PanelAssetBaseCommand

SKEY = "search_ref_palette"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

SRC_FILE_EXT = ".ref.md"
SRC_RAW_FILE_EXT = ".raw.ref.md"

def initSettings():
    defaultOptions = {
        #----------------- hidden setting ---------------------
        "project_src_basename": ".search_ref_palette",
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

class CaptureView(): # pylint: disable=R0903
    def __init__(self):
        self.isCapturingView = False
        self.view = None

    def onViewActivated(self, view):
        if self.isCapturingView:
            self.isCapturingView = False
            self.view = view


quickPanelView = CaptureView()
class SearchRefPaletteEventListener(sublime_plugin.EventListener):
    @staticmethod
    def on_post_save_async(view):
        pwa.onFileSave(view)

    @staticmethod
    def on_load_async(view):
        pwa.onFileLoad(view)

    @staticmethod
    def on_activated(view):
        quickPanelView.onViewActivated(view)

class RefKeyAssetManager(AssetSrcManager):
    def __init__(self, *arg):
        super().__init__(*arg)

    @staticmethod
    def vReportStatus(message):
        print(message)
        sublime.status_message(message)

    @staticmethod
    def vParseFile(srcFile):
        items = []
        if srcFile.path.endswith(SRC_RAW_FILE_EXT):
            rawItem = MarkDownInfo.HeaderItem()
            _, pathToken = pwa.getAssetHelpInfo(srcFile)
            rawItem.raw = "raw of {}".format(pathToken)
            rawItem.lineNum = 0
            rawItem.level = 0
            items.append(rawItem)
        else:
            items.extend(MarkDownInfo.parseFile(srcFile.path))

        for item in items:
            srcFile.appendAsset(item.raw, item)

    def vBuildAssetCat(self, asset):
        lkey, rkey = self.vBuildAssetKey(asset.orgKey, asset.val, asset.srcFile).split("\n")
        return rkey + "{:01000}".format(asset.val.level) + lkey

    @staticmethod
    def vBuildAssetKey(key, val, srcFile):
        headToken, pathToken = pwa.getAssetHelpInfo(srcFile)
        lkey = "[{level}]{key}".format(level=val.level, key=key)
        rkey = "{head_token}{path_token}".format(
            head_token=headToken, path_token=pathToken)

        return "\n".join([lkey, rkey])


pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = RefKeyAssetManager(SRC_FILE_EXT)
pwa.ps = ps
pwa.prjInfo = Project.ProjectInfo()

class SearchRefPaletteCommand(PanelAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vEndRun(self, panelData):
        self.window.run_command("create_pane", {"direction": "down", "give_focus": False})
        quickPanelView.isCapturingView = True
        return panelData

    @staticmethod
    def vPanelFlags():
        return sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST

    @staticmethod
    def vOpts(optKey):
        return pwa.opts(optKey)

    @staticmethod
    def vPrjInfo():
        return pwa.prjInfo

    @staticmethod
    def vConcreteAssets():
        return pwa.am.assets

    @staticmethod
    def vMakeAssetFileAsset():
        assetFileAssets = []
        for srcFile in pwa.am.srcFiles:
            cat = "key.dyn" if srcFile.isDyn else "key"
            virtualAssetToken = pwa.opts("virtual_asset_token")
            key = "".join([virtualAssetToken, cat])
            val = MarkDownInfo.HeaderItem()
            val.raw = key
            val.lineNum = 0
            val.level = 0
            assetKey = pwa.am.vBuildAssetKey(key, val, srcFile)
            assetFileAssets.append(Asset(assetKey, assetKey, val, srcFile))

        return assetFileAssets

    @staticmethod
    def getStrFileWithLineNum(asset):
        return "{0}:{1}".format(asset.srcFile.path, asset.val.lineNum)

    def onQuickPanelHighlight(self, index):
        asset = self.assetFromIndex(index)
        if asset is None:
            return

        self.window.focus_group(1)

        self.window.open_file(self.getStrFileWithLineNum(asset),
                              sublime.TRANSIENT|sublime.ENCODED_POSITION)

        self.window.focus_view(quickPanelView.view)

    def vInvokeAsset(self, asset):
        self.recoverPaneStatus()
        self.window.open_file(self.getStrFileWithLineNum(asset), sublime.ENCODED_POSITION)

    def vOnQuickPanelCancel(self):
        self.recoverPaneStatus()

    def recoverPaneStatus(self):
        self.window.focus_group(0)
        self.window.run_command("destroy_pane", {"direction": "down"})
        sublime.quickPanelView = None

