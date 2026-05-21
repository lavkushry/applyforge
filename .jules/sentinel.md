## 2024-05-24 - Path Traversal via Backslashes on POSIX
**Vulnerability:** User-uploaded filenames with backslashes (`\`) were bypassing `Path(filename).name` sanitization on POSIX systems, allowing path traversal attacks (e.g., `..\..\..\etc\passwd`).
**Learning:** `pathlib.Path` on POSIX systems does not recognize `\` as a directory separator, so it treats `..\etc\passwd` as a valid flat filename, failing to strip directory components.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename.replace("\\", "/")`) before passing user-uploaded filenames to `pathlib.Path` or similar path manipulation utilities on POSIX backends.
