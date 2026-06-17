## 2024-05-18 - Fix Path Traversal in File Uploads
**Vulnerability:** Path Traversal via unstripped backslashes in Python's `Path(filename).name` on POSIX systems.
**Learning:** Python's `pathlib.Path` does not normalize backslashes to forward slashes on POSIX systems, meaning filenames containing `\` (like `..\..\etc\passwd`) bypass name extraction and allow path traversal.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before parsing user-uploaded filenames with `Path`.
