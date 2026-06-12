## 2024-05-24 - Path Traversal via Backslash Evasion
**Vulnerability:** Path traversal in file uploads because backslashes are valid filename characters on POSIX systems but act as directory separators on Windows.
**Learning:** Using `Path(filename).name` without standardizing slashes fails to extract the safe name when a Windows-style path with backslashes is provided on a POSIX host.
**Prevention:** Always normalize backslashes to forward slashes before parsing filenames with `Path()`.
