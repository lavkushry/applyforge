## 2024-06-24 - Fix Path Traversal in File Uploads
**Vulnerability:** Path traversal and validation bypass in file uploads due to `Path(filename).name` and `Path(filename).suffix` not sanitizing backslashes on POSIX systems.
**Learning:** Python's `pathlib.Path` handles paths differently depending on the operating system. On POSIX systems, a backslash (`\`) is considered a valid character in a filename, not a directory separator. This allows attackers to bypass extension validation (e.g. `filename.pdf\evil.exe`) and potentially perform path traversal.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user-provided filenames to `Path` or OS-level file operations.
