

def runCommands(view, *cmds):
    for cmdName, cmdArgs in cmds:
        view.run_command(cmdName, cmdArgs)
