---
name: macOS Native Document Conversion
description: Pattern for using AppleScript instead of LibreOffice for document conversion on macOS.
---

# macOS Native Document Conversion

When working on this project (conversion_tool) on macOS, follow this architectural rule for converting Office and iWork documents to PDF:

1. **Do not use `LibreOffice` (`soffice --headless`) on macOS.**
2. **Use AppleScript (`osascript`)** to natively drive Microsoft Office (PowerPoint, Word, Excel) or Apple iWork (Keynote, Pages, Numbers).
3. Execute AppleScript by running Python's `subprocess.run(["osascript", "-e", script])`.
4. After generating a PDF on macOS, use `subprocess.Popen(["open", pdf_path])` to automatically preview it.
5. Provide robust error handling around `osascript` calls, since the host application might not be installed or authorized.

## Examples
**PowerPoint AppleScript Template:**
```applescript
set inFile to POSIX file "/absolute/path/to/input.pptx"
set outFile to POSIX file "/absolute/path/to/output.pdf"
tell application "Microsoft PowerPoint"
    open inFile
    save active presentation in outFile as save as PDF
    close active presentation saving no
end tell
```
