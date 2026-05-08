## 2025-02-14 - Fix Path Traversal in File Uploads
**Vulnerability:** Path traversal in `apps/api/app/services/files.py` via `save_upload` by missing normalization of backslashes before `Path(filename).name`.
**Learning:** `Path(filename).name` alone does not protect against Windows-style path traversal attacks (e.g., `..\..\..\etc\passwd`) when running on POSIX systems.
**Prevention:** Always normalize backslashes to forward slashes before extracting the base name and validate the extracted filename against an allowlist of safe characters using regex to mitigate crafted path risks.
