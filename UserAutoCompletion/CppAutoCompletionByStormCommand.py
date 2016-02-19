import sys
import sublime, sublime_plugin
# from .clang.cindex import Index
def get_unsaved_files(view):
    buffer = None
    buffer = [(view.file_name(), view.substr(sublime.Region(0, view.size())))]
    return buffer

def get_language(view):
    caret = view.sel()[0].a
    language = language_regex.search(view.scope_name(caret))
    if language != None:
        language = language.group(0)
    return language

class CppAutoCompleteByStorm(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        line, col = view.rowcol(locations[0])
        line += 1

        if len(prefix) == 0:
            col += 1


        curPos = locations[0]


        str = view.substr(sublime.Region(curPos - 100, curPos))
        # print("gg:"+str)








