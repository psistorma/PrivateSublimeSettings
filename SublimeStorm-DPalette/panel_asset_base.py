import sublime
import sublime_plugin
from SublimeUtils import Panel # pylint: disable=F0401
from MUtils import Str, Exp # pylint: disable=F0401
from MUtils.FileDataSrc import Asset

class IterInfo: # pylint: disable=R0903
    def __init__(self):
        self.iterNext = True
        self.iterAutoWrap = True
        self.iterHead = None

class AssetType:
    ASSET_TYPE_DUMMY, ASSET_TYPE_CONCRETE, ASSET_TYPE_VIRTUAL_FILE = range(-1, 2)

class PanelAssetBaseCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.dummyIndex = -1
        self.indexOfAssetMap = {}
        self.virutalAssets = None
        self.needLongPanel = True

    @Panel.fwShowQuickPanel()
    @Exp.fwReportException(sublime.error_message)
    def run(self, **kwds):
        self.vBeginRun(**kwds)
        return self.vEndRun(self._run(**kwds))

    def _run(self, **kwds):
        run_mode = kwds.get("run_mode", "panel")

        if run_mode == "key":
            key = kwds.get("key", None)
            self.invokeKey(key)
            return
        elif run_mode == "iter":
            iterInfo = IterInfo()
            iterInfo.iterNext = kwds.get("iter_next", iterInfo.iterNext)
            iterInfo.iterAutoWrap = kwds.get("iter_autowarp", iterInfo.iterAutoWrap)
            iterInfo.iterHead = kwds.get("iter_head", iterInfo.iterHead)
            self.iterKey(iterInfo)
            return
        elif run_mode == "repeat_lastkey":
            concreteAssets = self.vConcreteAssets()
            if len(concreteAssets) == 0:
                sublime.error_message("no asset yet, can't repeate last key!")
                return

            lastKey = self.vPrjInfo().tVal("last_key")
            if lastKey is None:
                lastKey = concreteAssets[-1].key

            self.invokeKey(lastKey)
            return
        elif run_mode != "panel":
            raise ValueError("run_mode: {} is not allowed", run_mode)

        view = self.window.active_view()
        selectedIndex = 1
        assets = self.filterAssets(view, self.allAssets())

        lastKey = self.vPrjInfo().tVal("last_key")
        if lastKey is not None:
            for idx, asset in enumerate(assets):
                if asset.key == lastKey:
                    selectedIndex = idx

        quickInvokeInfoArr = self.alignAssetKey(view, assets)
        self.dummyIndex = len(quickInvokeInfoArr)
        if self.needLongPanel:
            quickInvokeInfoArr.append(" "*500)

        return self, quickInvokeInfoArr, selectedIndex, self.vPanelFlags()

    def vBeginRun(self, **kwds):
        pass

    @staticmethod
    def vEndRun(panelData):
        return panelData

    @staticmethod
    def vPanelFlags():
        return sublime.MONOSPACE_FONT

    def allAssets(self):
        assets = self.vConcreteAssets()[::]
        self.virutalAssets = self.makeVirtualAssets()
        assets.extend(self.virutalAssets)
        for asset in assets:
            asset.key = asset.key.lower()

        return assets

    def vConcreteAssets(self):
        raise NotImplementedError()

    def makeVirtualAssets(self):
        virutalAssets = []
        virutalAssets.extend(self.vMakeAssetFileAsset())
        return virutalAssets

    @staticmethod
    def vMakeAssetFileAsset():
        return []

    def filterAssets(self, view, assets):
        filteredAssets = []
        assetKeyIdx = 0
        for idx, asset in enumerate(assets):
            if not self.vFilterAsset(view, asset):
                continue

            filteredAssets.append(asset)
            self.indexOfAssetMap[assetKeyIdx] = idx
            assetKeyIdx += 1

        return filteredAssets

    @staticmethod
    def vFilterAsset(_view, _asset): # pylint: disable=W0613
        return True

    @staticmethod
    def getLineNumerExt(view):
        lineCount = view.rowcol(view.size())[0] + 1
        return len(str(lineCount)) * 8.5

    def vOpts(self, optKey):
        raise NotImplementedError()

    def vPrjInfo(self):
        raise NotImplementedError()


    def alignAssetKey(self, view, assets):
        ext = view.viewport_extent()
        if self.needLongPanel:
            viewportRate = (ext[0]+self.getLineNumerExt(view))/self.vOpts("screen_param")
            panelWidth = int(viewportRate * self.vOpts("panel_param"))
        else:
            panelWidth = self.vOpts("panel_width")
        assetKeys = []
        for asset in assets:
            infoCount = len(asset.keyInfo) if asset.keyInfo else 0
            if infoCount == 0:
                assetKeys.append(asset.key)
            elif infoCount == 1:
                lkey, rkey = asset.key, asset.keyInfo[0]
                assetKeys.append(Str.alignmentBothSide(lkey, rkey, panelWidth))
            elif infoCount == 2:
                lkey, rkey, tip = asset.key, asset.keyInfo[0], asset.keyInfo[1]
                keyArr = [Str.alignmentBothSide(lkey, rkey, panelWidth)]
                tipArr = tip.split("\n")
                for idx in range(len(tipArr), 3):
                    tipArr.append("")
                keyArr.extend(tipArr[:3])
                assetKeys.append(keyArr)
            else:
                raise Exp.WrongCallError("key item count: {} is not support!".format(len(keyArr)))

        return assetKeys

    def assetFromIndex(self, index):
        if index == -1 or index == self.dummyIndex:
            return AssetType.ASSET_TYPE_DUMMY, None

        concreteAssets = self.vConcreteAssets()
        index = self.indexOfAssetMap[index]
        vitualIndex = index - len(concreteAssets)
        assetType = AssetType.ASSET_TYPE_CONCRETE
        if vitualIndex >= 0:
            asset = self.virutalAssets[vitualIndex]
            assetType = AssetType.ASSET_TYPE_VIRTUAL_FILE
        else:
            asset = concreteAssets[index]

        return assetType, asset

    def onQuickPanelDone(self, index):
        if index == -1:
            self.vOnQuickPanelCancel()
            return

        assetType, asset = self.assetFromIndex(index)
        if assetType == AssetType.ASSET_TYPE_DUMMY:
            return

        self.vInvokeAsset(asset, assetType)
        self.vPrjInfo().regItem("last_key", asset.key)

    def vOnQuickPanelCancel(self):
        pass

    def invokeKey(self, key):
        key = key.lower()
        for asset in self.allAssets():
            if asset.key == key:
                self.vInvokeAsset(asset, AssetType.ASSET_TYPE_CONCRETE)
                return

        sublime.error_message("key: {} is not found!" % key)

    def vInvokeAsset(self, asset, assetType):
        pass

    def iterKey(self, iterInfo):
        assets = []
        if iterInfo.iterHead is not None:
            for asset in self.vConcreteAssets():
                if asset.key.startswith(iterInfo.iterHead):
                    assets.append(asset)
        else:
            assets = self.vConcreteAssets()

        if len(assets) == 0:
            sublime.message_dialog("There is no key to iter yet!")
            return

        curIndex = 0
        prjInfo = self.vPrjInfo()

        lastIterIndex = prjInfo.val("last_iterIndex")
        if lastIterIndex is None:# last_iterIndex is for internal use now
            lastIterKey = prjInfo.val("last_iterkey")
            if lastIterKey is not None:
                for idx, asset in enumerate(assets):
                    if asset.key == lastIterKey:
                        curIndex = (idx + 1) if iterInfo.iterNext else (idx - 1)

            if curIndex == -1 or curIndex == len(assets):
                if not iterInfo.iterAutoWrap:
                    sublime.message_dialog("There is no key to iter yet, run again to wrap iter!")
                    prjInfo.regItem("last_iterIndex", curIndex, False)
                    return

            prjInfo.regItem("last_iterIndex", curIndex, None)
        else:
            curIndex = (lastIterIndex + 1) if iterInfo.iterNext else (lastIterIndex - 1)

        curIndex = curIndex % (len(assets))

        asset = assets[curIndex]
        self.vInvokeAsset(asset)
        prjInfo.regItem("last_iterkey", asset.key, False)

class PanelJsonAssetBaseCommand(PanelAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vProjectWiseAssetManager(self):
        raise NotImplementedError()

    def vOpts(self, optKey):
        return self.vProjectWiseAssetManager().opts(optKey)

    def vPrjInfo(self):
        return self.vProjectWiseAssetManager().prjInfo

    def vConcreteAssets(self):
        return self.vProjectWiseAssetManager().am.assets

    def vFormatAssetFileAssetKey(self, srcFile):
         pwa = self.vProjectWiseAssetManager()
         pathToken = pwa.assetPathToken(srcFile)
         cat = "key.dyn" if srcFile.isDyn else "key"
         virtualAssetToken = pwa.opts("virtual_asset_token")
         if pathToken:
            key = "".join([virtualAssetToken, cat, virtualAssetToken, pathToken])
         else:
            key = "".join([virtualAssetToken, cat])

         key = "{0}({1})".format(key, len(srcFile.assets))
         return key

    def vFormatAssetFileAssetVal(self, srcFile, key):
        raise NotImplementedError()

    def vMakeAssetFileAsset(self):
        pwa = self.vProjectWiseAssetManager()
        assetFileAssets = []
        for srcFile in pwa.am.srcFiles:
            key = self.vFormatAssetFileAssetKey(srcFile)
            val = self.vFormatAssetFileAssetVal(srcFile, key)

            key, *keyInfo = pwa.am.vBuildAssetKey(key, val, srcFile)
            assetFileAssets.append(Asset(key, key, val, srcFile, keyInfo))

        return assetFileAssets

