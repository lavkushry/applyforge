## 2024-05-24 - Path Traversal via Backslashes in User Uploads
**Vulnerability:** Path traversal vulnerability on POSIX systems where `Path(filename).name` failed to strip backslash directory traversal patterns (e.g., `..\..\..\`).
**Learning:** `pathlib.Path` handles paths according to the operating system it runs on. On POSIX systems, a backslash (`\`) is treated as a valid filename character, not a path separator. Thus, a filename like `..\..\file.txt` is treated as a single filename, which can bypass validation and lead to path traversal.
**Prevention:** Always normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before processing filenames with `Path` on backend servers handling user uploads.
