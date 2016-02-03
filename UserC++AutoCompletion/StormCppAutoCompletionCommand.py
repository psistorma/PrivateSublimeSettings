import sublime, sublime_plugin
import sys
from .clang.cindex import Index

class StormCppAutoCompletionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selections = self.view.sel()
    if len(selections) != 1:
      return

    import platform
    name = platform.system()
    print('ggggggggg:'+name)
    fileName = self.view.file_name()
    typeName = "CAboutDlg"
    print(fileName)

    for name, value in clangDll.enumerations.TokenKinds:
        print(name)
        print(value)

    region = selections[0]
    index = clangDll.clang.cindex.Index.create()
    tu = index.parse(fileName)
    print('Translation unit:' + tu.spelling)
    self.find_typerefs(tu.cursor, typeName)

  def find_typerefs(self, node, typename):
    """ Find all references to the type named 'typename'
    """
    if node.kind.is_reference():
        ref_node = clang.cindex.Cursor_ref(node)
        if ref_node.spelling == typename:
           print('Found {0} [line={1}, col={2}]'.format(
              typename, node.location.line, node.location.column))
    # Recurse for children of this node
    for c in node.get_children():
      find_typerefs(c, typename)

