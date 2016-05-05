from collections import namedtuple
import sublime
import sublime_plugin

def searchStrPos(view, fromPosition, content, search_ignorecase, isContentRegex):
    flags = 0
    if search_ignorecase:
        flags = flags or sublime.IGNORECASE

    if not isContentRegex:
        flags = flags or sublime.LITERAL

    foundRegion = view.find(content, fromPosition, flags)
    if foundRegion is None:
        return False, foundRegion.begin()
    else:
        return True, foundRegion.begin()

def searchToLineAnchor(view, basePos, forward):
    lineRegion = view.full_line(basePos)
    if forward:
        return sublime.Region(basePos, lineRegion.end())
    else:
        return sublime.Region(lineRegion.begin(), basePos+1)

ANCHOR_TYPE_PREV_CHAR = "prev_char"
ANCHOR_TYPE_NEXT_CHAR = "next_char"
ANCHOR_TYPE_CONTENT = "content"
ANCHOR_TYPE_SELECTION = "selection"

DIR_PREV = "prev"
DIR_NEXT = "next"

TO_ANCHOR = "anchor"
TO_LINE_ANCHOR = "line_anchor"

class ANCHAOR_CONFIG(object):
    def __init__(self):
        self.type = None
        self.content = None
        self.isRegex = False
        self.charCount = 1
        self.searchIgnorecase = False
        self.forward = True

class SelectToAnchorCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        anchorCfg = ANCHAOR_CONFIG()
        anchorCfg.type = args["anchor_type"]
        anchorCfg.isRegex = args.get("anchor_is_regex", False)
        if anchorCfg.type == ANCHOR_TYPE_CONTENT:
            anchorCfg.content = args.get("anchor_content", None)

        if anchorCfg.type == ANCHOR_TYPE_CONTENT and anchorCfg.content is None:
            raise ValueError("anchor_type is {0}, but anchor_content is not provided!"
                             .format(ANCHOR_TYPE_CONTENT))

        anchorCfg.charCount = args.get("anchor_char_count", 1)
        anchorCfg.searchIgnorecase = args.get("search_ignorecase", False)
        anchorCfg.forward = args.get("forward", True)

        to = args["to"]
        delete = args.get("delete", False)

        sels = self.view.sel()
        newRegions = []
        for region in sels:
            basePos = region.end()
            newRegion = None
            if TO_ANCHOR in to:
                searchContent = self.getSearchContent(self.view, basePos, region, anchorCfg)
                contentPos = self.searchToContent(self.view, basePos, searchContent, anchorCfg)

                if anchorCfg.forward:
                    newRegion = sublime.Region(region.end(), contentPos)
                else:
                    newRegion = sublime.Region(contentPos+len(searchContent), region.begin())

            if newRegion is not None:
                newRegions.append(newRegion)
                continue

            if TO_LINE_ANCHOR in to:
                newRegions.append(
                    searchToLineAnchor(self.view, basePos, anchorCfg.forward))

        if len(newRegions) == 0:
            sublime.status_message("can't found valid position!")
            return

        if delete:
            for region in newRegions:
                self.view.erase(edit, region)

            return

        sels.clear()
        for region in newRegions:
            sels.add(region)

    @staticmethod
    def getSearchContent(view, basePos, selRegion, anchorCfg):
        if anchorCfg.content:
            return anchorCfg.content

        contentRegion = None
        if anchorCfg.type == ANCHOR_TYPE_PREV_CHAR:
            contentRegion = sublime.Region(basePos-anchorCfg.charCount, basePos)
        elif anchorCfg.type == ANCHOR_TYPE_NEXT_CHAR:
            contentRegion = sublime.Region(basePos, basePos+anchorCfg.charCount)
        elif anchorCfg.type == ANCHOR_TYPE_SELECTION:
            contentRegion = selRegion
        else:
            raise ValueError("anchor_type: {} is not allowed!".format(anchorCfg.type))

        return view.substr(contentRegion)

    @staticmethod
    def searchToContent(view, basePos, searchContent, anchorCfg):
        lineRegion = view.full_line(basePos)
        search_frompos = basePos if anchorCfg.forward else lineRegion.begin()
        validPos = None
        while True:
            found, contentPos = searchStrPos(view, search_frompos,
                                             searchContent,
                                             anchorCfg.searchIgnorecase,
                                             anchorCfg.isRegex)
            if anchorCfg.forward:
                if found and contentPos >= lineRegion.end():
                    break

                validPos = contentPos
                break

            if not found:
                break

            search_frompos = contentPos + len(searchContent)
            if search_frompos >= basePos:
                break

            validPos = contentPos

        return validPos




