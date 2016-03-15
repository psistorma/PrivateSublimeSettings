from ..Base import RuleBase

class Selector(RuleBase):
    def __init__(self):
        super().__init__("selector")

    def isComplied(self, view, chkContent):
        return self._checkSel(
            view, chkContent,
            lambda view, sel, chkContent: view.match_selector(sel.a, chkContent.operand))
