## 2024-05-15 - CRITICAL Path Traversal in File Uploads
**Vulnerability:** User-uploaded filenames containing backslashes (e.g., `..\..\etc\passwd`) bypass path traversal sanitization on POSIX systems because `Path(filename).name` treats backslashes as regular filename characters.
**Learning:** `pathlib.Path` behaves differently on POSIX vs Windows. On POSIX, it only splits on forward slashes `/`. If user input contains backslashes, they are preserved in the filename, leading to potential traversal downstream if the path is later used in a Windows-like environment or parsed differently.
**Prevention:** Always normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user-uploaded filenames to `Path()`.
