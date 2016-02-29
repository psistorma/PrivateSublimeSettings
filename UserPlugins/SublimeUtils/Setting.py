from ..MUtils import Os
import sublime

def expandVariable(window, *strs, forSublime=True, forEnv=True):
    sublimeVariables = window.extract_variables()

    retStrs = [sublime.expand_variables(s, sublimeVariables)
               for s in strs] if forSublime else strs
    retStrs = Os.expandVariable(*retStrs) if forEnv else retStrs

    return retStrs


