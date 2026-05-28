## 2024-05-28 - Path Traversal via Backslashes on POSIX
**Vulnerability:** Path traversal using backslashes in user-uploaded filenames (e.g. `..\..\etc\passwd`).
**Learning:** `Path(filename).name` on POSIX systems treats backslashes as valid filename characters, not directory separators. Therefore, the backslashes are not stripped, and when the resulting string is concatenated with a directory path, it can lead to path traversal.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g. `filename.replace("\\", "/")`) before passing user-uploaded filenames to `Path()` or similar path manipulation functions.
