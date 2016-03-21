from collections import defaultdict
from . import WView

class ProjectInfoManager:
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
