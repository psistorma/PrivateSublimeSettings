import os
import unittest
from context import MarkDownInfo

class MDItemBuilder_TestCase(unittest.TestCase):
    def test_parseFile(self):
        mdItems = MarkDownInfo.parseFile(os.path.join(os.path.dirname(__file__), "MUtils_MarkDownInfo/test.md"))

        self.assertEqual(len(mdItems), 3)

        self.assertEqual(mdItems[0].type, MarkDownInfo.HEADER)
        self.assertEqual(mdItems[0].lineNum, 1)
        self.assertEqual(mdItems[0].level, 1)
        self.assertEqual(mdItems[0].raw, "Config multiple account for github in one pc")

        self.assertEqual(mdItems[1].type, MarkDownInfo.HEADER)
        self.assertEqual(mdItems[1].lineNum, 3)
        self.assertEqual(mdItems[1].level, 2)
        self.assertEqual(mdItems[1].raw, "1. [Generate ssh key](https://help.github.com/articles/generating-an-ssh-key/).")

        self.assertEqual(mdItems[2].type, MarkDownInfo.HEADER)
        self.assertEqual(mdItems[2].lineNum, 14)
        self.assertEqual(mdItems[2].level, 2)
        self.assertEqual(mdItems[2].raw, "2. [Setup multiple ssh account](http://code.tutsplus.com/tutorials/quick-tip-how-to-work-with-github-and-multiple-accounts--net-22574)")





if __name__ == '__main__':
    unittest.main()
