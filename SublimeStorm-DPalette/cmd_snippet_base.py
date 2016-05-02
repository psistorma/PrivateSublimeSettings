import re
import sublime
import sublime_plugin
from MUtils import Exp

class ManageSnippetBaseCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.snippetBase = None

    def run(self, **args):
        op = args["op"]

        if op == "setbase":
            self.opSetBase()
        elif op == "getbase":
            self.opGetBase(args)
        else:
            raise ValueError("op: {} is not allowed!".format(op))

    def opSetBase(self):
        content = sublime.get_clipboard()
        if content is None:
            raise ValueError("failed to get content from clipboard!")

        self.snippetBase = content.rstrip("\n\r")
        sublime.status_message("snippet base is set to: {}".format(self.snippetBase))

    def opGetBase(self, args):
        needTransform = args["transform"]
        needInsert = args["insert"]
        needClipboard = args["clipboard"]

        if self.snippetBase is None:
            raise Exp.WrongCallError("snippet base is not set yet!!")

        res = self._transform() if needTransform else self.snippetBase
        if needClipboard:
            sublime.set_clipboard(res)

        if needInsert:
            self.window.active_view().run_command("insert_snippet", {"contents": res})

    @staticmethod
    def regionToItems(sRegion):
        return sRegion.split("\n")

    def _transform(self):
        view = self.window.active_view()
        sels = view.sel()
        selItems = []
        for region in sels:
            sRegion = view.substr(region).strip("\n")
            selItems.append(self.regionToItems(sRegion))

        itemCount = None
        for items in selItems:
            if itemCount is None:
                itemCount = len(items)
            elif itemCount != len(items):
                raise ValueError("each selection region's item count is not same!")

        res = [self.snippetBase]*itemCount

        for grpIdx, items in enumerate(selItems):
            for itemIdx, item in enumerate(items):
                item = item.strip()
                if not item:
                    res[itemIdx] = ""
                    continue

                sResSnippet = res[itemIdx]
                sResSnippet = sResSnippet.replace("${}".format(grpIdx+1), item)
                sResSnippet = sResSnippet.replace("${{{pos}}}".format(pos=grpIdx+1), item)
                sPattern = r"\${{{pos}:.*?}}".format(pos=grpIdx+1)
                sResSnippet = re.sub(sPattern, item, sResSnippet)
                sResSnippet = sResSnippet.replace("$", "\$")
                res[itemIdx] = sResSnippet
                print(sResSnippet)

        return "\n".join(res)





