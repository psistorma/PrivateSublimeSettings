import unittest
import os
from context import FileDataSrc
from context import Str

class TestJsonManager(FileDataSrc.JsonAssetSrcManager):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.settings = {
            "palkey_path_token":
            "/",

            "project_palkey_path_token":
            ">",

            "dyn_token":
            "//",

            "project_dyn_token":
            ">>",

            "palette_width":
            100
        }

    def vReportStatus(self, message):
        print(message)

    def vBuildAssetKey(self, key, val, srcFile):
        return "".join(["key-", key, "-val-", val["val"], "-srcBasename-", srcFile.basename])

    @staticmethod
    def relPath(srcFile, srcDir):
        relPath = os.path.relpath(srcFile.path, srcDir.path)
        relPath = relPath.replace("\\", "/")
        return relPath

    def vBuildAssetCat(self, asset):
        return self.relPath(asset.srcFile, asset.srcFile.srcDir)

class JsonSrcManager_TestCase(unittest.TestCase):
    def test_getSpecifyKeyVal(self):
        srcManager = TestJsonManager(srcExt=".testjson", assetKey="assets", key="key")
        srcManager.loadStatic(os.path.join(os.path.dirname(__file__), "MUtils_FileDataSrc"))
        expectedKey = "".join(["key-", "lvl2-2-k1", "-val-", "I am lvl2-2 k1", "-srcBasename-", "lvl2-2.testjson"])
        keys = srcManager.keys()
        self.assertIn(expectedKey, keys)
        for idx, key in enumerate(keys):
            if key == expectedKey:
                asset = srcManager.asset(idx)
                self.assertEqual(asset.val["val"], "I am lvl2-2 k1")

if __name__ == '__main__':
    unittest.main()
