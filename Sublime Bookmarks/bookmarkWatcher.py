import sublime, sublime_plugin

class bookmarkWatcher(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        view_id = sublime.active_window().active_view().id()
        sublime.active_window().run_command("sublime_bookmark", {"type": "mark_buffer", "view_id": view_id} )
        sublime.active_window().run_command("sublime_bookmark", {"type": "move_bookmarks", "view_id": view_id} )


    def on_modified_async(self, view):
        view_id = sublime.active_window().active_view().id()
        sublime.active_window().run_command("sublime_bookmark", {"type": "move_bookmarks", "view_id": view_id} )


    def on_deactivated_async(self, view):
        # view_id = sublime.active_window().active_view().id()
        # sublime.active_window().run_command("sublime_bookmark", {"type": "mark_buffer", "view_id": view_id} )
        # sublime.active_window().run_command("sublime_bookmark", {"type": "move_bookmarks", "view_id": view_id} )
        pass

    #must be no close, not on pre close. on pre-close,the view still exists
    def on_close(self, view):
        sublime.active_window().run_command("sublime_bookmark", {"type": "update_temporary" } )

    def on_pre_save_async(self, view):
        pass
        #sublime.run_command("sublime_bookmark", {"type": "save_data" } )
