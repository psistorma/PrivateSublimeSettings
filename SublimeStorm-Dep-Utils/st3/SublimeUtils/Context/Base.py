import re
import sublime

class RuleBase:
    def __init__(self, key):
        self.key = key

    def isComplied(self, view, chkContent):
        pass

    @staticmethod
    def _isNegativeOperator(operator):
        return operator in [sublime.OP_NOT_EQUAL,
                            sublime.OP_NOT_REGEX_MATCH,
                            sublime.OP_NOT_REGEX_CONTAINS]

    @staticmethod
    def _checkValue(value, operator, operand):
        try:
            if operator == sublime.OP_EQUAL:
                return value == operand
            elif operator == sublime.OP_NOT_EQUAL:
                return value != operand
            elif operator == sublime.OP_REGEX_MATCH:
                return re.match(operand, value) is not None
            elif operator == sublime.OP_NOT_REGEX_MATCH:
                return re.match(operand, value) is None
            elif operator == sublime.OP_REGEX_CONTAINS:
                return re.search(operand, value) is not None
            elif operator == sublime.OP_NOT_REGEX_CONTAINS:
                return re.search(operand, value) is None
            else:
                raise Exception('Unsupported operator: ' + str(operator))
        except Exception as error:
            print('Failed to check context', operand, value, error)
            raise error


    def _checkWithVal(self, view, chkContent, callback):
        value = callback(view, chkContent)
        return self._checkValue(value, chkContent.operator, chkContent.operand)

    def _checkValueWithSel(self, view, chkContent, callback):
        def _checkValueSelResult(view, sel, chkContent):
            value = callback(view, sel, chkContent)
            return self._checkValue(value, chkContent.operator, chkContent.operand)

        return self._checkSel(view, chkContent, _checkValueSelResult)

    def _checkSel(self, view, chkContent, callback):
        result = True
        for sel in view.sel():
            result = callback(view, sel, chkContent)
            if self._isNegativeOperator(chkContent.operator):
                result = not result

            if result and not chkContent.match_all:
                return result

            if not result and chkContent.match_all:
                return result

        return result
