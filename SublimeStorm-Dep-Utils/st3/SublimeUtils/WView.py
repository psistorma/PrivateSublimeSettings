import functools as ft
import sublime

NO_PROJECT = "___NO_PROJECT_PRESENT____"

def fwPrepareWindow(f):
    @ft.wraps(f)
    def wapper(window, *args, **kwds):
        if window is None:
            window = sublime.active_window()

        return f(window, *args, **kwds)

    return wapper

def fwPrepareView(f):
    @ft.wraps(f)
    def wapper(view, *args, **kwds):
        if view is None:
            view = sublime.active_window().active_view()

        return f(view, *args, **kwds)

    return wapper

@fwPrepareWindow
def getProjectPath(window=None, lower=True):
    projectPath = window.project_file_name()
    if not projectPath:
        projectPath = NO_PROJECT

    return projectPath.lower()


