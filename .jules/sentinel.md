## 2023-10-24 - Path Traversal in File Upload
**Vulnerability:** User-uploaded filenames were parsed with `Path(filename).name` without stripping backslashes, allowing potential path traversal on POSIX systems.
**Learning:** Python's `pathlib.Path` treats backslashes as valid filename characters on POSIX systems, meaning a malicious payload like `..\..\secret` bypasses name extraction.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before parsing user-provided paths with `pathlib.Path`.
