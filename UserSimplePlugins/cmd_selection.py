import re
import sublime
import sublime_plugin

# <following reference from SelectUtil>
rSelector = re.compile(r"^(-?)(?:\{(-?\d+)\}|\[(.+)\]|/(.+)/)$")
def safe_end(region):
    if region is None:
        return -1
    return region.end()

def find_matching_point(view, sel, selector):
    result = rSelector.search(selector)

    if result is None: return False, safe_end(view.find(selector, sel.end(), sublime.LITERAL))

    groups = result.groups()
    isReverse = (groups[0] == "-")
    num = int(groups[1]) if groups[1] is not None else None
    chars = groups[2]
    regex = groups[3]

    if not isReverse:
        if num is not None: return isReverse, sel.end() + num
        elif regex is not None: return isReverse, safe_end(view.find(regex, sel.end()))
        else: return isReverse, safe_end(view.find(chars, sel.end(), sublime.LITERAL))

    else:
        if num is not None: return isReverse, sel.begin() - num
        elif regex is not None: regions = view.find_all(regex)
        else: regions = view.find_all(chars, sublime.LITERAL)

        for region in reversed(regions):
            if region.end() <= sel.begin():
                return isReverse, region.begin()

    return isReverse, -1
# </ following reference from SelectUtil>

class MoveBySideCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        extend = args.get("extend", False)
        count = args.get("count", 1)
        side = args.get("side", "both")
        target = args.get("target", None)

        selections = self.view.sel()
        newSels = []
        for region in selections:
            begin, end = region.begin(), region.end()
            if target is None:
                begin, end = self.expandByCount(region, side, count)
                if not extend:
                    if side == "left":
                        end = begin
                    elif side == "right":
                        begin = end
            else:
                isReverse, begin, end = self.expandByTarget(region, target, count)
                if not extend:
                    if isReverse:
                        end = begin
                    else:
                        begin = end

            if region.a <= region.b:
                newSels.append(sublime.Region(begin, end))
            else:
                newSels.append(sublime.Region(end, begin))

        selections.clear()
        for reg in newSels:
            selections.add(reg)

    def expandByTarget(self, region, target, count):
        baseBegin, baseEnd = region.begin(), region.end()
        isReverse = False
        for _ in range(0, count):
            baseRegion = sublime.Region(baseBegin, baseEnd)
            isReverse, newBeginEnd = find_matching_point(self.view, baseRegion, target)
            if isReverse:
                baseBegin = baseRegion.begin() if newBeginEnd == -1 else newBeginEnd
                baseEnd = baseRegion.end()
            else:
                baseBegin = baseRegion.begin()
                baseEnd = baseRegion.end() if newBeginEnd == -1 else newBeginEnd

        return isReverse, baseBegin, baseEnd

    @staticmethod
    def expandByCount(region, side, count):
        begin, end = region.begin(), region.end()

        if side == "both":
            begin -= count
            end += count
        elif side == "left":
            begin -= count
        elif side == "right":
            end += count
        else:
            raise ValueError('side is not valid, must be left,right,both')

        return begin, end


class CancelSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        cancel_from_end = args.get("cancel_from_end", 1)

        sels = self.view.sel()
        if len(sels) == 1:
            sel = sels[0]
            sel.b = sel.a
            sels.clear()
            sels.add(sel)
        else:
            remainSels = []
            for sel in sels:
                remainSels.append(sel)
            sels.clear()
            lenSels = len(remainSels)
            for idx, sel in enumerate(remainSels):
                if idx == lenSels - cancel_from_end:
                    continue
                sels.add(sel)



