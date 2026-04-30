## 2024-05-18 - Path Traversal Vulnerability in File Uploads
**Vulnerability:** Path traversal possible through `save_upload` in `apps/api/app/services/files.py`.
**Learning:** `Path(filename).name` is insufficient to prevent path traversal on POSIX systems because it does not properly normalize backslashes (`\`) into forward slashes (`/`), potentially allowing attackers to write files outside the intended directory.
**Prevention:** Always manually normalize backslashes to forward slashes, and strip any remaining relative path attempts (`.`), while keeping only a safe subset of characters.