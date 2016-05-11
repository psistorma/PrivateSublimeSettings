import os
import json
import sys
import jsoncfg
from . import Exp, Os

class Asset:
    def __init__(self, orgKey, key, val, srcFile, keyInfo = None):
        self.orgKey = orgKey
        self.key = key
        self.val = val
        self.keyInfo = keyInfo
        self.srcFile = srcFile

class SrcObj:
    def __init__(self, path, parent=None):
        self.path = os.path.normpath(path).lower()
        self.parent = parent
        self.items = []

    def load(self):
        raise NotImplementedError()

    @property
    def manager(self):
        return self.parent.manager

    @property
    def basename(self):
        return os.path.basename(self.path)

    def isMe(self, path):
        return Os.isSameFile(self.path, path)

class SrcFile(SrcObj):
    def __init__(self, filePath, isDyn, srcDir):
        super().__init__(filePath, srcDir)
        self.isDyn = isDyn

    @property
    def assets(self):
        return self.items

    @property
    def srcDir(self):
        return self.parent

    def appendAsset(self, key, val):
        alterKey, *keyInfo  = self.buildAssetKey(key, val)
        self.items.append(Asset(key, alterKey, val, self, keyInfo))

    def reBuildAssetKey(self):
        for asset in self.assets:
            asset.key = self.buildAssetKey(asset.orgKey, asset.val)

    def buildAssetKey(self, key, val):
        alterKey, *keyInfo = self.manager.vBuildAssetKey(key, val, self)
        if alterKey is None:
            alterKey = key

        retList = []
        retList.append(alterKey)
        retList.extend(keyInfo)
        return retList

    def load(self):
        self.assets.clear()
        self.manager.vParseFile(self)
        self.manager.vReportStatus("file: {} is loaded".format(self.path))

    def dump(self):
        if not self.isDyn:
            raise Exp.WrongCallError("static file: {} can't be dump!".format(self.path))

        assetDict = {}
        for asset in self.assets:
            assetDict[asset.key] = asset.val

        json.dump(assetDict, self.path)


class SrcDir(SrcObj):
    def __init__(self, dirPath, isStatic, manager):
        super().__init__(dirPath, manager)
        self.isStatic = isStatic

    @property
    def manager(self):
        return self.parent

    @property
    def srcFiles(self):
        return self.items

    @property
    def assets(self):
        return [asset for srcFile in self.srcFiles for asset in srcFile.assets]

    def load(self):
        self.srcFiles.clear()
        manager = self.manager
        files = Os.fetchFiles(self.path, manager.srcExt, manager.includeSubDir)
        for f in files:
            srcFile = SrcFile(f, manager.vIsDynFile(f), self)
            srcFile.load()
            self.srcFiles.append(srcFile)

        self.manager.vReportStatus("dir: {} is loaded".format(self.basename))
        return len(files) > 0

class AssetSrcManager:
    def __init__(self, srcExt, *, includeSubDir=True, maxCacheProjectCount=5):
        self.srcExt = srcExt
        self.includeSubDir = includeSubDir
        self.maxCacheProjectCount = maxCacheProjectCount
        self.srcDirs = []
        self.assets = None
        self.projectSrc = None

    def vAssetSortkey(self, asset):
        """ can be overrided """
        srcFile = asset.srcFile
        srcDir = srcFile.srcDir
        priorityKeys = []
        if srcDir.isStatic:
            priorityKeys.append(1)
        else:
            priorityKeys.append(0)

        priorityKeys.append(self.vBuildAssetCat(asset))
        priorityKeys.append(asset.key)
        return priorityKeys

    def vBuildAssetCat(self, asset):
        """ can be overrided """
        pass

    def vIsDynFile(self, srcFilePath):
        """ can be overrided """
        return False

    def vBuildAssetKey(self, key, val, srcFile):
        """ can be overrided """
        pass

    def vParseFile(self, srcFile):
        raise NotImplementedError()

    def vReportStatus(self, message):
        """ can be overrided """
        pass

    def loadStatic(self, srcDirPath):
        srcDirPath = srcDirPath.lower()
        self.srcDirs = [srcDir for srcDir in self.srcDirs if not srcDir.isMe(srcDirPath)]
        self.loadSrcDir(srcDirPath)
        self.collectAssets()

    def removeSrc(self, *, static=True):
        self.srcDirs = [srcDir for srcDir in self.srcDirs if srcDir.isStatic != static]
        self.collectAssets()

    def switchProject(self, projectAssetPath):
        isKeyRebuilded = False
        projectAssetPath = projectAssetPath.lower()
        if self.projectSrc is not None and self.projectSrc.isMe(projectAssetPath):
            return isKeyRebuilded

        projectSrcCount = len([srcDir for srcDir in self.srcDirs if not srcDir.isStatic])
        if projectSrcCount > self.maxCacheProjectCount:
            needPurgeCount = projectSrcCount - self.maxCacheProjectCount
            purgedSrcDirs = []
            for src in self.srcDirs[::-1]:
                if src.isStatic or needPurgeCount == 0:
                    purgedSrcDirs.append(src)
                else:
                    needPurgeCount -= 1

            self.srcDirs = purgedSrcDirs[::-1]

        self.projectSrc = self.loadSrcDir(projectAssetPath, False)
        self.collectAssets()
        isKeyRebuilded = True

        return isKeyRebuilded

    def refreshFile(self, filePath):
        filePath = os.path.normpath(filePath).lower()
        for srcFile in self.srcFiles:
            if srcFile.isMe(filePath):
                srcFile.load()
                self.collectAssets()
                return True

        for srcDir in self.srcDirs:
            if filePath.startswith(srcDir.path):
                srcDir.load()
                self.collectAssets()
                return True

        return False

    def loadSrcDir(self, srcDirPath, isStatic=True):
        self.assets = None
        newSrcDir = SrcDir(srcDirPath, isStatic, self)
        newSrcDir.load()
        self.srcDirs.append(newSrcDir)
        return newSrcDir

    def updateSrcDir(self, srcDirPath):
        for srcDir in self.srcDirs:
            if srcDir.isMe(srcDirPath):
                srcDir.load()
                return True

        return False

    def collectAssets(self):
        collectSrcDirs = [src for src in self.srcDirs
                          if src.isStatic or self.projectSrc is src]

        self.assets = [asset for srcDir in collectSrcDirs
                       for asset in srcDir.assets]

        self.assets.sort(key=self.vAssetSortkey)
        self.vOnFinishCollectAssets()

    @property
    def srcFiles(self):
        return [srcFile for srcDir in self.srcDirs for srcFile in srcDir.srcFiles]

    def reBuildAssetKey(self):
        for srcFile in self.srcFiles:
            srcFile.reBuildAssetKey()

        self.collectAssets()

    def vOnFinishCollectAssets(self):
        """ can be overrided """
        pass

    def keys(self):
        return [asset.key for asset in self.assets]

    def asset(self, index):
        return self.assets[index]


class JsonAssetSrcManager(AssetSrcManager):
    def __init__(self, *, assetKey="assets", key="key", **kwds):
        super().__init__(**kwds)
        self.assetKey = assetKey
        self.key = key

    def vParseFile(self, srcFile):
        cfg = jsoncfg.load(srcFile.path)
        for asset in cfg[self.assetKey]:
            srcFile.appendAsset(asset[self.key], asset)
