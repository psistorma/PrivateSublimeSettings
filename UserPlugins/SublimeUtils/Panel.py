import sublime

def showInputPanel(window, onDone, title="", initText="", *, onChange=None, onCancel=None):
    if not window:
        window = sublime.active_window()

    window.show_input_panel(
        title, initText, onDone, onChange, onCancel)
