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


class NewGroupPane:
    def __init__(self, direction="down"):
        self.isCapturingView = False
        self.view = None
        self.direction = direction

    def onViewActivated(self, view):
        if self.isCapturingView:
            self.isCapturingView = False
            self.view = view

    def startPane(self):
        sublime.active_window().run_command(
                    "create_pane", {"direction": self.direction, "give_focus": False})
        self.isCapturingView = True

    def endPane(self):
        window = sublime.active_window()
        window.focus_group(0)
        window.run_command("destroy_pane", {"direction": self.direction})
        self.view = None

    def openFileTransient(self, filePath, lineNum):
        window = self.view.window()
        window.focus_group(1)

        if lineNum is None:
            window.open_file(filePath, sublime.TRANSIENT)
        else:
            window.open_file("{0}:{1}".format(filePath, lineNum),
                              sublime.TRANSIENT | sublime.ENCODED_POSITION)

        window.focus_view(self.view)
        sublime.set_timeout(lambda: window.focus_view(self.view), 500)
