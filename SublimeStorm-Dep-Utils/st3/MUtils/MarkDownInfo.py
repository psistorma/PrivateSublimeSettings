import difflib
import mistune

_debug = False
def _debugPrint(header, info, width=80, fillChar="-"):
    if _debug:
        print(" debug[{}] ".format(header).center(width, fillChar))
        print(info)

fnDbgReport = _debugPrint

(
    BLOCK_CODE, BLOCK_QUOTE, BLOCK_HTML, HEADER, HRULE, LIST, LIST_ITEM, PARAGRAPH, TABLE,
    TABLE_ROW, TABLE_CELL, AUTOLINK, CODESPAN, DOUBLE_EMPHASIS, EMPHASIS, IMAGE, LINEBREAK,
    NEWLINE, LINK, STRIKETHROUGH, TEXT, INLINE_HTML
) = (
    "block_code", "block_quote", "block_html", "header", "hrule", "list", "list_item",
    "paragraph", "table", "table_row", "table_cell", "autolink", "codespan", "double_emphasis",
    "emphasis", "image", "linebreak", "newline", "link", "strikethrough", "text", "inline_html"
)

class Item:
    def __init__(self):
        self.type = None
        self.lineNum = 0

class HeaderItem(Item):
    def __init__(self, *arg):
        super().__init__(*arg)
        self.text = None
        self.level = 0
        self.raw = None

class MDItemBuilder(mistune.Renderer):
    def __init__(self, *arg):
        super().__init__(*arg)
        self.items = []
        self.lines = None
        self.lineNumDict = None

    def header(self, text, level, raw=None):
        item = HeaderItem()
        item.type = HEADER
        item.text = text
        item.level = str(level)
        item.raw = raw

        matchList = difflib.get_close_matches(item.raw, self.lines)
        item.lineNum = self.lineNumDict[matchList[0]] if matchList else 0
        self.items.append(item)
        fnDbgReport("markdown item info", "{0} ### level: {1} type: {2} line: {3}".format(
            item.raw, item.level, item.type, item.lineNum))
        return ""


def parseFile(filePath):
    fnDbgReport("parse file path", filePath)

    lines = []
    with open(filePath) as f:
        for l in f:
            lines.append(l)

    return parseContent(lines)

def parseContent(lines):
    lineNumDict = {}
    for lineNum, line in enumerate(lines, 1):
        lineNumDict[line] = lineNum

    sLines = "".join(lines)
    fnDbgReport("file content", sLines)

    builder = MDItemBuilder()
    builder.lines = lines
    builder.lineNumDict = lineNumDict

    markdown = mistune.Markdown(renderer=builder)
    markdown(sLines)
    return builder.items

