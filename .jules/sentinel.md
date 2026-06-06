## 2024-05-15 - Path Traversal via Un-normalized Backslashes
**Vulnerability:** User-uploaded filenames containing backslashes (e.g., `..\..\..\etc\passwd`) were not stripped or handled safely on POSIX systems when passed to `Path(filename).name`, leading to potential path traversal vulnerabilities.
**Learning:** Python's `pathlib.Path` behaves according to the underlying OS. On POSIX, a backslash is a valid filename character and doesn't act as a directory separator, meaning `Path("..\\..\\..\\etc\\passwd").name` returns the whole string rather than the base name.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename.replace("\\", "/")`) before passing user-uploaded filenames to `pathlib.Path()` for parsing or validation.
