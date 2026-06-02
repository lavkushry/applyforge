## 2024-05-18 - Path Traversal via Backslash on POSIX
**Vulnerability:** The codebase was susceptible to path traversal attacks during file uploads on POSIX systems because `Path(filename).name` was used to sanitize the filename, but backslashes (`\`) are treated as valid filename characters on POSIX and not stripped.
**Learning:** Python's `pathlib.Path` behaves differently depending on the operating system. On POSIX systems, it does not recognize backslashes as path separators, allowing attackers to bypass `.name` sanitization by injecting backslashes (e.g., `..\..\etc\passwd`).
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before parsing with `Path` or use a dedicated secure filename utility.
