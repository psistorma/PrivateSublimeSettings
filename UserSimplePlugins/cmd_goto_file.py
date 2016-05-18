import os
import re
import sublime
import sublime_plugin
from SublimeUtils import Setting

FILE_REGEX_ARR = [
    "(?i)^\\s*File\\s*:?\\s*(?:\"|')?(.+?)(?:\"|')?,\\s*line\\s*:?\\s*([0-9]+)",
    "(?i)^(\\w+\\.ts)\\(([0-9]+),[0-9]+\\):"
]

class GotoFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        lineRegion = self.view.full_line(self.view.sel()[0].begin())
        sLine = self.view.substr(lineRegion)
        for filePattern in FILE_REGEX_ARR:
            res = re.match(filePattern, sLine)
            if res is None:
                continue
            filePath = res.group(1)
            line = res.group(2)
            if not os.path.exists(filePath):
                fileDirectory, = Setting.expandVariables(window, "${file_path}")
                filePath = os.path.join(fileDirectory, filePath)
                if not os.path.exists(filePath):
                    continue

            window.open_file("{0}:{1}".format(filePath, line), sublime.ENCODED_POSITION)
            return

        sublime.status_message("can't find file!")
