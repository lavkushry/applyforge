## 2025-02-24 - Fix Path Traversal in File Uploads using secure_filename
**Vulnerability:** Path traversal vulnerability in `apps/api/app/services/files.py` where `save_upload` was extracting the file name using `Path(filename).name`, which does not strip backslashes (`\`) on POSIX systems, allowing arbitrary file writes.
**Learning:** `Path(filename).name` is insufficient for securely processing user-uploaded file names because it does not handle Windows-style path separators (`\`) when running on POSIX systems.
**Prevention:** Always manually normalize backslashes to forward slashes, apply regex allowlists, and strip leading dots before extracting the base name for any user-uploaded files, such as by using a dedicated `secure_filename` function.
