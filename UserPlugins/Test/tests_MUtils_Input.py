import unittest
from context import Input

class promiseInput_TestCase(unittest.TestCase):
    def test_notMatch(self):
        case = ({"inStr": "Input.sub  :  important",
                 "pattern": r"^notMatch.*?\s+:\s+.*$"
                },
                None)
        self.assertEqual(Input.promiseInput(**case[0]), case[1])

    def test_match(self):
        case = ({"inStr": "Input.sub  :  important",
                 "pattern": r"^.*?\s+:\s+.*$",
                },
                "Input.sub  :  important")
        self.assertEqual(Input.promiseInput(**case[0]), case[1])

    def test_matchWithTransTempate(self):
        case = ({"inStr": "Input.sub  :  important",
                 "pattern": r"^(?P<info>.*?)\s+:\s+(?P<tip>.*)$",
                 "transTemplate": "info: {{info}}\ntip: {{tip}}",
                },
                "info: Input.sub\ntip: important")
        self.assertEqual(Input.promiseInput(**case[0]), case[1])


    def test_matchWithDefaultDict(self):
        case = ({"inStr": "Input.sub with default",
                 "pattern": r"^(?P<info>[^:]*)(\s+:\s+(?P<tip>.*))?$",
                 "transTemplate": "info: {{info}}\ntip: {{tip}}",
                 "defaultDict": {"tip": "normal case"}
                },
                "info: Input.sub with default\ntip: normal case")

        self.assertEqual(Input.promiseInput(**case[0]), case[1])

if __name__ == '__main__':
    unittest.main()
