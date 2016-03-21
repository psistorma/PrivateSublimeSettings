import sublime
from . import Data, SubModuleLoader, WView
from .Base import RuleBase

class _Context():
    def __init__(self):
        self.ruleLoader = None
        self.ruleDict = {}
        self.operators = None
        self._init()

    def _init(self):
        self.ruleLoader = SubModuleLoader.Loader('rule', '.rules', __package__)

        self.operators = {
            'equal': sublime.OP_EQUAL,
            'not_equal': sublime.OP_NOT_EQUAL,
            'regex_match': sublime.OP_REGEX_MATCH,
            'not_regex_match': sublime.OP_NOT_REGEX_MATCH,
            'regex_contains': sublime.OP_REGEX_CONTAINS,
            'not_regex_contains': sublime.OP_NOT_REGEX_CONTAINS,
        }

    def check(self, view, context):
        result, operator = True, "and"
        for item in context:
            if isinstance(item, str):
                operator = item
                continue

            if isinstance(item, list):
                result = self._mergeResult(operator, result, self.check(view, item))
                continue

            checkResult = self._checkItem(view, item)
            result = self._mergeResult(operator, result, checkResult)

        return result

    def getRule(self, key):
        rule = self.ruleDict.get(key, None)
        if rule is not None:
            return rule

        ruleTypes = self.ruleLoader.fetchModule(key).objByBaseType(RuleBase)
        ruleTypeLen = len(ruleTypes)
        if ruleTypeLen == 0:
            raise ValueError("rule for context:{} is not exist!", key)

        if ruleTypeLen > 1:
            raise ValueError("multi rule for context:{} exist!", key)

        rule = ruleTypes[0]()
        self.ruleDict[key] = rule
        return rule

    def _checkItem(self, view, item):
        key, chkContent = self._prepareCheckContent(item)
        rule = self.getRule(key)
        return rule.isComplied(view, chkContent)

    @staticmethod
    def _mergeResult(operator, result, current):
        if operator == "and":
            return result and current
        elif operator == "or":
            return result or current

        raise Exception('Operator should be "or" or "and"; given: ' + operator)

    def _prepareCheckContent(self, item):
        key = item['key'].lower()
        operator = self.operators[item['operator'].lower()]
        operand = item['operand']
        match_all = item.get('match_all', False)

        return key, Data.toNamedTuple(
            "operator, operand, match_all",
            operator, operand, match_all)

contextObject = _Context()
@WView.fwPrepareView
def check(view, context):
    return contextObject.check(view, context)

