## 2026-06-13 - Path Traversal Prevention
**Vulnerability:** Path traversal in `Path(filename).name` on POSIX systems when filenames contain backslashes.
**Learning:** Backslashes are not stripped on POSIX systems, allowing attackers to upload files with malicious backslash paths that could be processed insecurely.
**Prevention:** Always normalize backslashes to forward slashes `filename.replace("\\", "/")` before parsing filenames with `Path`.
