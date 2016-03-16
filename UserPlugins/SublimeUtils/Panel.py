import functools as ft
import sublime
from . import WView

def fwShowQuickPanel(timeout=10):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            ret = f(*args, **kwds)
            if ret is None:
                return

            self, items, selected_index, *flagArg = ret
            if flagArg:
                flags, = flagArg
            else:
                flags = 0

            on_done, on_highlight = None, None
            metaOfSelf = dir(self)
            if "onQuickPanelDone" in metaOfSelf:
                on_done = self.onQuickPanelDone

            if "onQuickPanelHighlight" in metaOfSelf:
                on_highlight = self.onQuickPanelHighlight

            showQuickPanel(
                None, items, on_done, timeout,
                on_highlight=on_highlight, flags=flags, selected_index=selected_index)

        return wrapper

    return decorator

@WView.fwPrepareWindow
def showInputPanel(window, onDone, title="", initText="", *, onChange=None, onCancel=None):
    window.show_input_panel(
        title, initText, onDone, onChange, onCancel)

@WView.fwPrepareWindow
def showQuickPanel(window, items, on_done, timeout=10, **kwds):
    if timeout:
        sublime.set_timeout(lambda: window.show_quick_panel(items, on_done, **kwds), timeout)
    else:
        window.show_quick_panel(items, on_done, **kwds)
