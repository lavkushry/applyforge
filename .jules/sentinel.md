## 2025-02-27 - Path Traversal Vulnerability in File Uploads
**Vulnerability:** The `save_upload` function in `apps/api/app/services/files.py` relied on `Path(filename).name` which did not properly sanitize paths containing backslashes on POSIX systems, exposing a path traversal vector.
**Learning:** `Path(filename).name` is platform-dependent and insufficient for sanitizing user-supplied file names on POSIX when given Windows-style paths (e.g. `..\..\etc\passwd`).
**Prevention:** Implemented and used a robust `secure_filename` function that explicitly replaces backslashes with forward slashes, uses regex allowlisting (`[^a-zA-Z0-9.\-_]`), and strips leading dots before processing uploads.
