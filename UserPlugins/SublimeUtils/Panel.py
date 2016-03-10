import functools as ft
import sublime

def fwShowQuickPanel(timeout=10):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            self, items, selected_index, *flags = f(*args, **kwds)
            if flags:
                flags, = flags



            showQuickPanel(None, items, on_done, timeout,
                           on_highlighted=on_highlighted, selected_index=selected_index)

        return wrapper

    return decorator

def _fwPrepareWindow(f):
    @ft.wraps(f)
    def wapper(window, *args, **kwds):
        if not window:
            window = sublime.active_window()

        return f(window, *args, **kwds)

    return wapper

@_fwPrepareWindow
def showInputPanel(window, onDone, title="", initText="", *, onChange=None, onCancel=None):
    window.show_input_panel(
        title, initText, onDone, onChange, onCancel)

@_fwPrepareWindow
def showQuickPanel(window, items, on_done, timeout=10, **kwds):
    if timeout:
        sublime.set_timeout(lambda: window.show_quick_panel(items, on_done, **kwds), timeout)
    else:
        window.show_quick_panel(items, on_done, **kwds)
