import unittest
from context import Os

class fetchFiles_TestCase(unittest.TestCase):
    def test_fetchPalKey(self):
        files = Os.fetchFiles("E:\\ForDevEnv\\anotherPalette", ".anotherpal.key")
        self.assertIn("E:\\ForDevEnv\\anotherPalette\\default.dyn.anotherpal.key", files)


if __name__ == '__main__':
    unittest.main()
