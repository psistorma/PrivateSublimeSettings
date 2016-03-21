import functools as ft
import sublime
from . import WView

def fwForMultiSelection(needRegularRegion=True):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(view, *args, **kwds):
            rets = []
            for orgRegion in view.sel():
                region = orgRegion
                if needRegularRegion:
                    region = regularRegion(orgRegion)

                rets.append(f(region, orgRegion, view, *args, **kwds))

            return rets

        return wrapper

    return decorator

def regularRegion(region):
    return region if region.a <= region.b else sublime.Region(region.b, region.a)

@fwForMultiSelection()
@WView.fwPrepareView
def getRowCols(region=None, _=None, view=None):
    return view.rowcol(region.a)

@fwForMultiSelection()
@WView.fwPrepareView
def getSelTexts(region=None, _=None, view=None):
    return view.substr(region)

@fwForMultiSelection()
@WView.fwPrepareView
def getLeftTexts(region=None, _=None, view=None):
    lineRegion = view.line(region.a)
    return view.substr(sublime.Region(lineRegion.a, region.a))

@fwForMultiSelection()
@WView.fwPrepareView
def getRightTexts(region=None, _=None, view=None):
    return view.substr(region.b)

@fwForMultiSelection()
@WView.fwPrepareView
def getLines(region=None, _=None, view=None):
    return view.substr(view.line(region.a))
