import os
from collections import defaultdict
from MUtils import Os
import sublime
from . import WView

class ProjectInfo:
    def __init__(self):
        self.globalInfo = defaultdict(lambda: None)
        self.prjInfoMap = defaultdict(lambda: defaultdict(lambda: None))

    @staticmethod
    def prjKey(window=None):
        return WView.getProjectPath(window)

    def info(self, window=None):
        return self.prjInfoMap[self.prjKey(window)]

    def regItem(self, key, val, alsoUpdateGlobal=True):
        self.info()[key] = val
        if alsoUpdateGlobal:
            self.globalInfo[key] = val

    def val(self, key, defVal=None):
        return self.info().get(key, defVal)

    def gVal(self, key, defVal=None):
        return self.globalInfo.get(key, defVal)

    def tVal(self, key, defVal=None):
        prjInfo = self.info()

        if key in prjInfo:
            return prjInfo[key]

        if key in self.globalInfo:
            return self.globalInfo[key]

        return defVal

@WView.fwPrepareWindow
def getProjectAuxiDirectory(window, fileDirectoryName, *, makeIfNotExist=False):
    project = WView.getProjectPath(window)
    if project is None:
        return None

    workDir, prjFileName = os.path.split(project)
    prjName, _ = os.path.splitext(prjFileName)
    auxiPath = os.path.join(workDir, fileDirectoryName, prjName)
    if makeIfNotExist and not os.path.exists(auxiPath):
        Os.promiseDirectory(auxiPath)

    return auxiPath

class ProjectWiseAsset:
    def __init__(self, srcExt):
        self.am = None
        self.ps = None
        self.prjInfo = None
        self.srcExt = srcExt


    def opts(self, optKey):
        return self.ps.opts[optKey]

    def prevOpts(self, optKey):
        return self.ps.prevOpts[optKey]

    @property
    def metaDynFileName(self):
        return "default.dyn" + self.srcExt

    @property
    def metaHiddenAssetToken(self):
        return "hidden-"

    def isDynFile(self, srcFilePath):
        return os.path.basename(srcFilePath).lower() == self.metaDynFileName

    def isHidden(self, key):
        return key.lower().startswith(self.metaHiddenAssetToken)

    def getDynAssetFilePath(self, assetDirectory):
        return os.path.join(assetDirectory, self.metaDynFileName)

    def getStaticAssetDirectory(self):
        return self.opts("palkey_path")

    def getProjectAssetDirectory(self, window, *, makeIfNotExist=False):
        return getProjectAuxiDirectory(
            window, self.opts("project_src_basename"), makeIfNotExist=makeIfNotExist)

    def assetPathToken(self, assetSrcFile):
        if self.isDynFile(assetSrcFile.path):
            return ""

        relPath = os.path.relpath(assetSrcFile.path, assetSrcFile.srcDir.path)
        relPath = relPath.replace("\\", "/")
        return os.path.dirname(relPath)

    def getAssetHelpInfo(self, srcFile, tip):
        pathToken = self.assetPathToken(srcFile)
        headToken, tipToken = "", ""
        tip = tip or ""

        if srcFile.srcDir.isStatic:
            if srcFile.isDyn:
                headToken = self.opts("dyn_token")
            else:
                headToken = self.opts("palkey_path_token")
        else:
            if srcFile.isDyn:
                headToken = self.opts("project_dyn_token")
            else:
                headToken = self.opts("project_palkey_path_token")

        tipToken = self.opts("palkey_path_token")

        if tip and pathToken:
            tip = tipToken + tip

        return headToken, pathToken, tip

    def refreshStaticAssets(self):
        isKeyRebuilded = False
        curPalkeyPath = self.opts("palkey_path")
        if not os.path.exists(curPalkeyPath):
            msg = "can't visit path: {}!".format(curPalkeyPath)
            sublime.error_message(msg)
            raise ValueError(msg)

        if curPalkeyPath == self.prevOpts("palkey_path"):
            return isKeyRebuilded

        self.am.loadStatic(curPalkeyPath)
        isKeyRebuilded = True

        return isKeyRebuilded

    def refreshProjectAssets(self, window):
        prjAssetPath = self.getProjectAssetDirectory(window)
        if os.path.exists(prjAssetPath):
            isKeyRebuilded = self.am.switchProject(prjAssetPath)
        else:
            self.am.projectSrc = None
            self.am.collectAssets()
            isKeyRebuilded = False

        return isKeyRebuilded

#   event util followed
    def onOptionChanged(self):
        isKeyRebuilded = False
        if self.refreshStaticAssets():
            isKeyRebuilded = True

        if self.refreshProjectAssets(sublime.active_window()):
            isKeyRebuilded = True

        if not isKeyRebuilded:
            self.am.reBuildAssetKey()

    def onFileSave(self, view):
        variables = view.window().extract_variables()
        _file = variables["file"].lower()
        if _file.endswith(self.srcExt):
            self.am.refreshFile(_file)

    def onFileLoad(self, view):
        self.refreshProjectAssets(view.window())
