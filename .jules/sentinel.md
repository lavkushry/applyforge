## 2024-10-24 - [Path Traversal via Backslashes on POSIX]
**Vulnerability:** Path traversal vulnerability due to un-normalized backslashes in user-provided filenames not being stripped by `Path(filename).name` on POSIX systems.
**Learning:** Python's `pathlib.Path` treats backslashes (`\`) as valid filename characters on POSIX, allowing path traversal if they are not explicitly replaced or normalized.
**Prevention:** Always manually normalize backslashes to forward slashes before parsing filenames with `Path` when handling user input.
