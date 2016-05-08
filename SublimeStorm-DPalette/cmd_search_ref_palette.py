import os
import sublime_plugin
import sublime
from SublimeUtils import Setting, Panel, Project
from MUtils import Os, Str, Data, Input, Exp, MarkDownInfo
from MUtils.FileDataSrc import AssetSrcManager, Asset
from .panel_asset_base import PanelAssetBaseCommand

SKEY = "search_ref"
ps = Setting.PluginSetting(SKEY)
def plugin_loaded():
    initSettings()

def plugin_unloaded():
    ps.onPluginUnload()

SRC_FILE_EXT = ".md"

def initSettings():
    defaultOptions = {
        #----------------- hidden setting ---------------------
        "project_src_basename": ".search_ref",
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

class RefKeySrcManager(AssetSrcManager):
    def __init__(self, *arg):
        super().__init__(*arg)

    @staticmethod
    def vReportStatus(message):
        print(message)
        sublime.status_message(message)

    def vParseFile(self, srcFile):
        items = MarkDownInfo.parseFile(srcFile.path)
        for item in items:
            srcFile.appendAsset(item.raw, item)

    @staticmethod
    def vBuildAssetKey(key, val, srcFile):
        headToken, pathToken = pwa.getAssetHelpInfo(srcFile)
        rkey = "{head_token}{path_token}[{level}]".format(
            head_token=headToken, level=val.level, path_token=pathToken)

        return "\n".join([key, rkey])


pwa = Project.ProjectWiseAsset(srcExt=SRC_FILE_EXT)
pwa.am = RefKeySrcManager(SRC_FILE_EXT)
pwa.ps = ps
pwa.prjInfo = Project.ProjectInfo()


class SearchRefPaletteCommand(PanelAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def vPanelFlags():
        return sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST

    def vOpts(self, optKey):
        return pwa.opts(optKey)

    def vPrjInfo(self):
        return pwa.prjInfo

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
            val = MarkDownInfo.HeaderItem()
            val.raw = key
            val.lineNum = 0
            val.level = 0
            assetKey = pwa.am.vBuildAssetKey(key, val, srcFile)
            assetFileAssets.append(Asset(assetKey, assetKey, val, srcFile))

        return assetFileAssets

    def onQuickPanelHighlight(self, index):
        if index == 0:
            self.window.open_file("E:/Tmp/test.cpp:36", sublime.TRANSIENT|sublime.ENCODED_POSITION)
        else:
            self.window.open_file("E:/Tmp/test.py:2", sublime.TRANSIENT|sublime.ENCODED_POSITION)

# # class AnotherPaletteEventListener(sublime_plugin.EventListener):
# #   def on_post_save(self, view):
# #     variables = view.window().extract_variables()
# #     _file = variables['file'].lower()
# #     if _file.endswith('.anotherpal.key'):
# #       gKeyDict.refresh()

# def fwShowQuickPanel(timeout=10):
#     def decorator(f):
#         @ft.wraps(f)
#         def wrapper(*args, **kwds):
#             self, items, selected_index, *flagArg = f(*args, **kwds)
#             if flagArg:
#                 flags, = flagArg
#             else:
#                 flags = 0

#             on_done, on_highlight = None, None
#             metaOfSelf = dir(self)
#             if "onQuickPanelDone" in metaOfSelf:
#                 on_done = self.onQuickPanelDone

#             if "onQuickPanelHighlight" in metaOfSelf:
#                 on_highlight = self.onQuickPanelHighlight

#             Panel.showQuickPanel(
#                 None, items, on_done, timeout,
#                 on_highlight=on_highlight, flags=flags, selected_index=selected_index)

#         return wrapper

#     return decorator


# class AnotherPaletteCommand(sublime_plugin.WindowCommand):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.lastPalKey = None

#         self.palKeyArr = None
#         self.curHighlight = -1
#     @fwShowQuickPanel(0)
#     def run(self, need_pane=True, highlight_index=-1, **kwds):
#         if need_pane:
#             self.window.run_command("create_pane", {"direction": "down", "give_focus": False})
#         selectedIndex = 1
#         quickInvokeInfoArr = [
#         ["to github" + " "*145 + "/src/go/to/school/hello/hi/devSublimePlugins !to github",
#         "/devSublimePlugins!to github"],
#         ["to github super" + " "*125 + "/src/go/to/school/hello/hi/devSublimePlugins !to github super",
#         "/devSublimePlugins!to github super"],
#         # ["to github", ">devSublimePlugins!to github"],
#         # ["to github", "//!to github"],
#         [" " * 250, "C"]
#         # ["to github", ">>!to github"],
#         ]
#         # quickInvokeInfoArr = [["A", "B"], [" " * 5000, "C"]]
#         # quickInvokeInfoArr = [["A", "B"], ["C", " " * 500]]
#         if highlight_index != -1:
#             selectedIndex = highlight_index

#         return self, quickInvokeInfoArr, selectedIndex
#     def onQuickPanelDone(self, index):
#         if index == -1:
#             return

#         self.window.run_command("destroy_pane", {"direction": "down"})
#         self.window.focus_group(0)
#         if index == 0:
#             self.window.open_file("E:/Tmp/1.txt:36", sublime.TRANSIENT|sublime.ENCODED_POSITION)
#         else:
#             self.window.open_file("E:/Tmp/test.py:16", sublime.TRANSIENT|sublime.ENCODED_POSITION)

#     def onQuickPanelHighlight(self, index):
#         if self.curHighlight == index:
#             return

#         self.curHighlight = index
#         self.window.focus_group(1)

#         if index == 0:
#             self.window.open_file("E:/Tmp/1.txt:36", sublime.TRANSIENT|sublime.ENCODED_POSITION)
#         else:
#             self.window.open_file("E:/Tmp/test.py:16", sublime.TRANSIENT|sublime.ENCODED_POSITION)
#         self.window.focus_group(0)

#         self.window.run_command("another_palette", {"need_pane":False, "highlight_index":index})

