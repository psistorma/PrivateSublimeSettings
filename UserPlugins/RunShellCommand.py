import shlex
import subprocess
import sublime_plugin

from . import Scommon


class RunShellCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        cmd = args['cmd']
        shlex.split(cmd)
        cmd = Scommon.expandVariable(self.window, cmd)

        process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output = process.communicate()
        if process.returncode:
            print("The options_script failed with code [%s]" % process.returncode)
            print(output[1])
        else:
            opts += shlex.split(bdecode(output[0]))
        for region in selections:
          selText = self.view.substr(region)
          selText = selText.replace("\\", "\\\\")
          self.view.replace(edit, region, selText)





