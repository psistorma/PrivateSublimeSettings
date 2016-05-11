import os
import json
import fn
import sublime
import sublime_plugin
from SublimeUtils import Panel, Setting # pylint: disable=F0401
from MUtils import Str, Exp, Input, Data # pylint: disable=F0401

class RecordContentBaseCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args):
        super().__init__(*args)
        self.transfKey = None
        self.transfVal = None
        self.ignoreKeys = None
        self.qAndaDict = None
        self.need_expand_variables = None

    @Input.fwAskQuestions(
        fn.F(Panel.showInputPanel, None),
        fn.F(sublime.message_dialog, "Canceled on answering question!"))
    @Exp.fwReportException(sublime.error_message)
    def run(self, qAndaDict=None, **kwds):
        content = kwds.get("content")
        ignore_target = kwds.get("ignore_target", [])
        self.transfKey = "key" not in ignore_target
        self.transfVal = "val" not in ignore_target
        self.ignoreKeys = kwds.get("ignore_keys", [])
        self.need_expand_variables = kwds.get("need_expand_variables", True)
        belong_to_project = kwds.get("belong_to_project", False)
        record_mode = kwds.get("record_mode", "record")
        self.qAndaDict = qAndaDict

        key = content["key"]
        if self.qAndaDict is not None:
            key = Str.renderText(key, **self.qAndaDict)

        key = key.lower()
        if record_mode == "erase":
            self.vEraseContent(key, belong_to_project)
            return
        elif record_mode == "toggle":
            self.vEraseContent(key, belong_to_project)
        elif record_mode == "record":
            pass
        else:
            sublime.error_message(
                "record_mode: {} is not allowed".format(record_mode))

        self.vPreTransContent(key, content)
        content = Data.transfJsonObj(content, self.needTransf, self.transf)
        self.vPostTransContent(content)

        self.vRecordContent(key, content, belong_to_project)

    def vPreTransContent(self, key, content):
        pass

    def vPostTransContent(self, content):
        pass

    def needTransf(self, obj, isKey):
        if isKey:
            if not self.transfKey:
                return False

            if obj in self.ignoreKeys:
                return False

            return False

        if not isKey and not self.transfVal:
            return False

        return isinstance(obj, str)

    def transf(self, obj, _):
        if self.qAndaDict is not None:
            obj = Str.renderText(obj, **self.qAndaDict)

        if self.need_expand_variables:
            obj, = Setting.expandVariables(self.window, obj)

        return obj

    def vEraseContent(self, key, belong_to_project):
        pass

    def vRecordContent(self, key, content, belong_to_project):
        pass

class RecordJsonAssetBaseCommand(RecordContentBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vEraseContent(self, key, belong_to_project):
        recordFilePath = self.vGetRecordFilePath(belong_to_project)
        if not os.path.exists(recordFilePath):
            return

        with open(recordFilePath, "r") as f:
            contentDict = json.load(f)

        if not self.filterOutContent(contentDict, key):
            return

        self.vSaveRecordFile(recordFilePath, contentDict, belong_to_project)

    def vRecordContent(self, key, content, belong_to_project):
        recordFilePath = self.vGetRecordFilePath(belong_to_project)
        contentDict = {self.vMetaSectionKey: []}
        if os.path.exists(recordFilePath):
            try:
                with open(recordFilePath, "r") as f:
                    contentDict = json.load(f)
            except Exception as e:
                sublime.error_message(
                    "parse file:\n{0}\nerror:\n{1}".format(recordFilePath, str(e)))

            self.filterOutContent(contentDict, key)

        contentDict[self.vMetaSectionKey].append(content)
        self.vSaveRecordFile(recordFilePath, contentDict, belong_to_project)

    def filterOutContent(self, contentDict, key):
        filtered = [content for content in contentDict[self.vMetaSectionKey]
                    if content[self.vMetaItemKey].lower() != key]

        if len(filtered) != len(contentDict[self.vMetaSectionKey]):
            contentDict[self.vMetaSectionKey] = filtered
            return True

        return False

    @property
    def vMetaSectionKey(self):
        return "assets"

    @property
    def vMetaItemKey(self):
        return "key"

    def vGetRecordFilePath(self, belong_to_project):
        raise NotImplementedError()

    def vSaveRecordFile(self, recordFilePath, contentDict, belong_to_project):
        raise NotImplementedError()


class ProjectWiseJsonAssetRecordBaseCommand(RecordJsonAssetBaseCommand):
    def __init__(self, *args):
        super().__init__(*args)

    def vProjectWiseAssetManager(self):
        raise NotImplementedError()

    def vGetRecordFilePath(self, belong_to_project):
        pwa = self.vProjectWiseAssetManager()
        if belong_to_project:
            assetDirectory = pwa.getProjectAssetDirectory(self.window, makeIfNotExist=True)
        else:
            assetDirectory = pwa.getStaticAssetDirectory()

        return pwa.getDynAssetFilePath(assetDirectory)

    def vSaveRecordFile(self, recordFilePath, contentDict, belong_to_project):
        pwa = self.vProjectWiseAssetManager()
        isFileExist = os.path.exists(recordFilePath)

        with open(recordFilePath, "w") as f:
            json.dump(contentDict, f, indent=4)

        if isFileExist:
            pwa.am.refreshFile(recordFilePath)
        else:
            if belong_to_project:
                pwa.refreshProjectAssets(self.window)
            else:
                pwa.am.loadStatic(recordFilePath)

