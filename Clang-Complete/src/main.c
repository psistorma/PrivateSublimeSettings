#include <stdlib.h>
#include <clang-c/Index.h>
#include <stdio.h>

#include "cc_symbol.h"
#include "cc_result.h"
enum CXChildVisitResult vit(CXCursor cursor,
	CXCursor parent,
	CXClientData client_data)
{
	unsigned line, col, offset;
	unsigned sline, scol, soffset;
	unsigned eline, ecol, eoffset;
	unsigned rline, rcol, roffset;
	CXSourceLocation loc = clang_getCursorLocation(cursor);
	CXSourceRange ext = clang_getCursorExtent(cursor);
	CXCursor cRef = clang_getCursorReferenced(cursor);
	CXSourceLocation rloc = clang_getCursorLocation(cRef);

	CXSourceLocation locStart = clang_getRangeStart(ext);
	CXSourceLocation locEnd = clang_getRangeEnd(ext);
	CXFile locFile, rLocFile;
	clang_getSpellingLocation(loc, &locFile, &line, &col, &offset);
	const char* sLocFile = clang_getCString(clang_getFileName(locFile));
	if (sLocFile == NULL)
		return CXChildVisit_Continue;

	clang_getSpellingLocation(locStart, NULL, &sline, &scol, &soffset);
	clang_getSpellingLocation(locEnd, NULL, &eline, &ecol, &eoffset);
	clang_getSpellingLocation(rloc, &rLocFile, &rline, &rcol, &roffset);
	const char* srLocFile = clang_getCString(clang_getFileName(rLocFile));
	CXType t = clang_getCursorType(cursor);
	CXCursor dclCursor = clang_getTypeDeclaration(t);
	CXType rt = clang_getCursorType(dclCursor);
	if (line > 150)
	{

		int a = 3;
		a = 5;
	}
	if (t.kind != CXType_Invalid)
	{
		CXString ts = clang_getTypeSpelling(t);
		const char* cs = clang_getCString(ts);
		cs = NULL;
	}
	return CXChildVisit_Continue;
}
int main()
{
	//const char* filename = "E:\\Tmp\\TestMake\\TestMake\\test.cpp";
	const char* filename = "E:\\Tmp\\TestMake\\TestMake\\TestMake.cpp";
	const char* opt[12] = {
		"-isystem", "C:\\Program Files (x86)\\Windows Kits\\8.1\\Include\\um",
		"-isystem", "C:\\Program Files (x86)\\Windows Kits\\8.1\\Include\\shared",
		"-isystem", "C:\\Program Files (x86)\\Windows Kits\\8.1\\Include\\winrt",
		"-isystem", "C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\include",
		"-isystem", "C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\atlmfc\\include",
		"-isystem", "C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.10150.0\\ucrt",
	};
	struct cc_symbol* sp = cc_symbol_new(filename, NULL, 0, NULL, 0);
	CXCursor cursor = clang_getTranslationUnitCursor(sp->tu);
	clang_visitChildren(cursor, vit, NULL);
	return 0;

	struct cc_result* rp = cc_symbol_complete_at(sp, 154, 9, NULL, 0);
	//struct cc_result* rp = cc_symbol_complete_at(sp, 33, 25, NULL, 0);
	struct match_result ret = cc_result_match(rp, "Person");
	// cc_result_dump(rp, ret);  // for test
	cc_result_free(rp);
	cc_symbol_free(sp);
  return 0;
}
