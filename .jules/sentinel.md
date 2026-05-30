## 2024-05-24 - Path Traversal via Backslashes on POSIX
**Vulnerability:** Path traversal and extension bypass on POSIX systems via backslashes in user-uploaded filenames.
**Learning:** Python's `Path(filename).name` and `Path(filename).suffix` do not strip path components separated by backslashes (`\`) on POSIX systems, treating them as valid filename characters.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user-provided filenames to `Path`.
