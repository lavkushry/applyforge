## 2024-05-18 - Prevent path traversal via normalized filenames
**Vulnerability:** Filenames with backslashes are not properly sanitized by `Path(filename).name` on POSIX systems.
**Learning:** Python's `pathlib.Path` behaves differently depending on the operating system. On POSIX, backslashes are valid filename characters and are not stripped by `.name`.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before parsing with `Path`.
