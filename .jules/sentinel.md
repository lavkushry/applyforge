## 2025-02-09 - Fix Path Traversal Vulnerability in File Uploads
**Vulnerability:** User-uploaded filenames were parsed using `Path(filename).name` without normalizing backslashes, allowing attackers to bypass directory stripping on POSIX systems using Windows-style paths (e.g., `..\..\`).
**Learning:** `pathlib.Path` uses the operating system's native path separator. On POSIX systems, it does not recognize backslashes as directory separators, treating them as valid filename characters instead.
**Prevention:** Always normalize backslashes to forward slashes (`filename.replace("\\", "/")`) before passing untrusted filenames to `pathlib.Path`.
