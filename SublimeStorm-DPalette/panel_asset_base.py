import sublime
import sublime_plugin
from SublimeUtils import Panel # pylint: disable=F0401
from MUtils import Str, Exp # pylint: disable=F0401

class IterInfo: # pylint: disable=R0903
    def __init__(self):
        self.iterNext = True
        self.iterAutoWrap = True
        self.iterHead = None

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
        elif run_mode != "panel":
            raise ValueError("run_mode: {} is not allowed", run_mode)

        view = self.window.active_view()
        selectedIndex = 1
        assets = self.filterAssets(view, self.vAssets())

        lastKey = self.vPrjInfo().tVal("last_key")

        if lastKey is not None:
            for idx, asset in enumerate(assets):
                if asset.key == lastKey:
                    selectedIndex = idx

        quickInvokeInfoArr = self.alignAssetKey(view, assets)
        self.dummyIndex = -1
        self.dummyIndex = len(quickInvokeInfoArr)
        if self.needLongPanel:
            quickInvokeInfoArr.append(" "*500)

        return self, quickInvokeInfoArr, selectedIndex, self.vPanelFlags()

    @staticmethod
    def vPanelFlags():
        return sublime.MONOSPACE_FONT

    def vAssets(self):
        raise NotImplementedError()

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
        viewportRate = (ext[0]+self.getLineNumerExt(view))/self.vOpts("screen_param")
        panelWidth = int(viewportRate * self.vOpts("panel_param"))
        assetKeys = []
        for asset in assets:
            keyArr = asset.key.split("\n")
            if len(keyArr) == 1:
                assetKeys.append(keyArr[0])
            elif len(keyArr) == 2:
                [lkey, rkey] = keyArr
                assetKeys.append(Str.alignmentBothSide(lkey, rkey, panelWidth))
            else:
                raise Exp.WrongCallError("key item count: {} is not support!".format(len(keyArr)))

        return assetKeys

    def onQuickPanelDone(self, index):
        if index == -1 or index == self.dummyIndex:
            return

        concreteAssets = self.vConcreteAssets()
        index = self.indexOfAssetMap[index]
        vitualIndex = index - len(concreteAssets)
        if vitualIndex >= 0:
            asset = self.virutalAssets[vitualIndex]
        else:
            asset = concreteAssets[index]

        self.vInvokeAsset(asset)
        self.vPrjInfo().regItem("last_palkey", asset.key)

    def invokeKey(self, key):
        key = key.lower()
        for asset in self.vAssets():
            if asset.key == key:
                self.vInvokeAsset(asset)
                return

        sublime.error_message("key: {} is not found!" % key)

    def vInvokeAsset(self, asset):
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

