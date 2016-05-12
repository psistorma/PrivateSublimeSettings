import os
import sublime_plugin
import sublime
from SublimeUtils import Setting, Project,WView  # pylint: disable=F0401
from MUtils import MarkDownInfo  # pylint: disable=F0401
from MUtils.FileDataSrc import AssetSrcManager, Asset  # pylint: disable=F0401
from .panel_asset_base import PanelAssetBaseCommand,AssetType

SKEY = "search_ref_palette"
SRC_FILE_EXT = ".ref.md"
SRC_RAW_FILE_EXT = ".raw.ref.md"

def plugin_loaded():
    defOpts = defaultOptions()
    pwa.onPluginLoaded(SKEY, defOpts)

def plugin_unloaded():
    pwa.onPluginUnload()

def defaultOptions():
    return {
        #----------------- hidden setting ---------------------
        "project_src_basename": ".search_ref_palette",
        "virtual_asset_token": "~",
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
            rawItem.raw = pathToken
            rawItem.lineNum = 0
            rawItem.level = -1
            items.append(rawItem)
        else:
            try:
                items.extend(MarkDownInfo.parseFile(srcFile.path))
            except Exception as e:  # pylint: disable=W0703
                sublime.error_message("error when parse file:\n{0}\nerror:\n{1}"
                                      .format(srcFile.path, str(e)))

        for item in items:
            srcFile.appendAsset(item.raw, item)

    def vBuildAssetCat(self, asset):
        lkey, rkey = self.vBuildAssetKey(
            asset.orgKey, asset.val, asset.srcFile)
        sLevel = "{:01000}".format(
            asset.val.level) if asset.val.level != 0 else "-----"
        return rkey + sLevel + lkey

    @staticmethod
    def vBuildAssetKey(key, val, srcFile):
        headToken, pathToken = pwa.getAssetHelpInfo(srcFile)
        if val.level > 0:
            lkey = "[{level}]{key}".format(level=val.level, key=key)
        elif val.level == -1:
            lkey = "[r]{key}".format(key=key)
        else:
            lkey = "[-]{key}".format(key=key)

        rkey = "{head_token}{path_token}".format(
            head_token=headToken, path_token=pathToken)

        return [lkey, rkey]

class SearchRefPaletteCommand(PanelAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vEndRun(self, panelData):
        quickPanelView.startPane()
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
    def vFormatAssetFileAssetVal(srcFile, key):
        val = MarkDownInfo.HeaderItem()
        val.raw = key
        val.lineNum = 0
        val.level = 0
        return val

    def onQuickPanelHighlight(self, index):
        assetType, asset = self.assetFromIndex(index)
        if assetType == AssetType.ASSET_TYPE_DUMMY:
            return

        quickPanelView.openFileTransient(asset.srcFile.path, asset.val.lineNum)

    def vInvokeAsset(self, asset, _):
        quickPanelView.endPane()
        self.window.open_file(
            "{0}:{1}".format(asset.srcFile.path, asset.val.lineNum),
            sublime.ENCODED_POSITION)

    def vOnQuickPanelCancel(self):
        quickPanelView.endPane()

pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = RefKeyAssetManager(SRC_FILE_EXT)
pwa.ps = Setting.PluginSetting(SKEY)
pwa.prjInfo = Project.ProjectInfo(SKEY)

quickPanelView = WView.NewGroupPane()
