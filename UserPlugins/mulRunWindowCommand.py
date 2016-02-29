import sublime
import sublime_plugin

class MulRunWindowCommand(sublime_plugin.WindowCommand):
    def exec_command(self, command):
        if not 'command' in command:
            raise Exception('No command name provided.')

        args = None
        if 'args' in command:
            args = command['args']

        # default context is the window since it's easiest to get the other contexts
        # from the view
        context = self.window
        if 'context' in command:
            context_name = command['context']
            if context_name == 'text':
                context = context.active_view()
            elif context_name == 'app':
                context = sublime
            elif context_name == 'window':
                pass
            else:
                raise Exception('Invalid command context "'+context_name+'".')

        # skip args if not needed
        if args is None:
            context.run_command(command['command'])
        else:
            context.run_command(command['command'], args)

    def run(self, **args):
        commands = args["commands"]
        for command in commands:
            self.exec_command(command)
