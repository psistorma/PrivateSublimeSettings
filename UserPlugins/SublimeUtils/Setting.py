from MUtils     import Os
from sublime    import expand_variables

def expandVariable(window, *strs, forSublime=True, forEnv=True):
    sublimeVariables = window.extract_variables()
    retStrs = [lambda s: expand_variables(s, sublimeVariables)
               for s in strs] if forSublime else strs

    retStrs = Os.expandVariable(retStrs) if forEnv else retStrs

    return retStrs


