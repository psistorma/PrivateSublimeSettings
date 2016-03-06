import unittest
from MUtils import Basic

class promiseInput_TestCase(unittest.TestCase):
    def test_notMatch(self):
        case = ({"inStr": "Basic.sub  :  important",
                 "pattern": r"^notMatch.*?\s+:\s+.*$"
                },
                None)
        self.assertEqual(Basic.promiseInput(**case[0]), case[1])

    def test_match(self):
        case = ({"inStr": "Basic.sub  :  important",
                "pattern": r"^.*?\s+:\s+.*$",
                },
                "Basic.sub  :  important")
        self.assertEqual(Basic.promiseInput(**case[0]), case[1])

    def test_matchWithTransTempate(self):
        case = ({"inStr": "Basic.sub  :  important",
                 "pattern": r"^(?P<info>.*?)\s+:\s+(?P<tip>.*)$",
                 "transTemplate": "info: {{info}}\ntip: {{tip}}",
                },
                "info: Basic.sub\ntip: important")
        self.assertEqual(Basic.promiseInput(**case[0]), case[1])


    def test_matchWithDefaultDict(self):
        case = ({"inStr": "Basic.sub",
                 "pattern": r"^(?P<info>\S*)(\s+:\s+(?P<tip>.*))?$",
                 "transTemplate": "info: {{info}}\ntip: {{tip}}",
                 "defaultDict": {"tip": "normal case"}
                },
                "info: Basic.sub\ntip: normal case")

        self.assertEqual(Basic.promiseInput(**case[0]), case[1])



if __name__ == '__main__':
    unittest.main()
