# import re
import sublime_plugin
import sublime
from .SublimeUtils import Setting, Panel
from MUtils import Os, Str, Data, Input, Exp, MarkDownInfo
from MUtils.FileDataSrc import JsonSrcManager, Asset
# import functools as ft

# def plugin_loaded():
#     pass

# def plugin_unloaded():
#     pass
PROJECT_SRC_BASENAME = ".search_ref"
DYN_SRC_FILENAME = "default.dyn.md"
HIDDEN_ASSET_TOKEN = "hidden-"

class RefKeySrcManager(SrcManager):
    def __init__(self, *arg):
        super().__init__(*arg)

    def reportStatus(self, message):
        print(message)
        sublime.status_message(message)

    def parseFile(self, srcFile):
        items = MarkDownInfo.parseFile(srcFile.path)
        for item in items:
            srcFile.appendAsset(item.raw, item)

    @staticmethod
    def isDynFile(srcFilePath):
        return os.path.basename(srcFilePath).lower() == DYN_REF_FILENAME

    @staticmethod
    def buildAssetKey(key, val, srcFile):
        return Rm.makeAssetKey(key, val.level, srcFile)

    @staticmethod
    def pathToken(srcFile):
        if Rm.isDynFile(srcFile.path):
            return ""

        relPath = os.path.relpath(srcFile.path, srcFile.srcDir.path)
        relPath = relPath.replace("\\", "/")
        return os.path.dirname(relPath)

    @staticmethod
    def makeAssetKey(key, level, srcFile):
        pathToken = Rm.pathToken(srcFile)

        rkey = "".join(["[{}]".format(level), "[{}: ]".format(pathToken), key])
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
            Os.promiseDirectory(assetPath)

        return assetPath

    @staticmethod
    def getStaticAssetPath():
        return ps.opts["refkey_path"]

    @staticmethod
    def getDynAssetFile(assetPath):
        return os.path.join(assetPath, DYN_SRC_FILENAME)

    @staticmethod
    def isHidden(key):
        return key.lower().startswith(HIDDEN_ASSET_TOKEN)

Rm = PalKeySrcManager(SRC_FILE_EXT)

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

