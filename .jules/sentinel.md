## 2024-05-27 - Path Traversal via Backslash on POSIX
**Vulnerability:** Path traversal possible during file upload by using backslashes (e.g., `..\..\etc\passwd`) when deploying on a POSIX system.
**Learning:** `Path(filename).name` in Python on a POSIX system treats backslashes as regular filename characters, not directory separators, failing to sanitize the path correctly and allowing backslashes to reach the target path generation.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename.replace("\\", "/")`) before parsing with `Path()` for file uploads.
