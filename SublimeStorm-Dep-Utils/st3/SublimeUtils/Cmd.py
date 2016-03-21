

def runCommands(ctx, *cmds):
    for cmdName, cmdArgs in cmds:
        ctx.run_command(cmdName, cmdArgs)

