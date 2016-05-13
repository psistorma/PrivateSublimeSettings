import functools as ft
import sublime
from MUtils import Os # pylint: disable=F0401

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

    return projectPath.lower() if lower else projectPath



class NewGroupPane:
    def __init__(self, direction="down"):
        self.isCapturingView = False
        self.view = None
        self.direction = direction
        self.orgActiveGroup = None
        self.group = None

    def onViewActivated(self, view):
        if self.isCapturingView:
            self.isCapturingView = False
            self.view = view

    def startPane(self):
        actveiWindow = sublime.active_window()
        self.orgActiveGroup = actveiWindow.active_group()
        self.group = actveiWindow.num_groups()

        actveiWindow.run_command(
            "create_pane", {"direction": self.direction, "give_focus": False})
        self.isCapturingView = True

    def endPane(self):
        window = sublime.active_window()
        window.focus_group(self.orgActiveGroup)
        window.run_command("destroy_pane", {"direction": self.direction})
        self.view = None
        self.group = None
        self.orgActiveGroup = None

    def openFileTransient(self, filePath, lineNum):
        window = self.view.window()
        window.focus_group(self.group)

        if lineNum is None:
            window.open_file(filePath, sublime.TRANSIENT)
        else:
            window.open_file("{0}:{1}".format(filePath, lineNum),
                             sublime.TRANSIENT | sublime.ENCODED_POSITION)

        window.focus_view(self.view)
        def promiseViewCondition():
            window.focus_view(self.view)

            if any(Os.isSameFile(filePath, v.file_name())
                   for v in window.views_in_group(self.group)):
                return

            for grp in [grp for grp in range(0, window.num_groups()) if grp != self.group]:
                for v in window.views_in_group(grp):
                    if Os.isSameFile(filePath, v.file_name()):
                        window.set_view_index(v, self.group, 0)
                        window.focus_view(self.view)
                        return

        sublime.set_timeout(promiseViewCondition, 500)
