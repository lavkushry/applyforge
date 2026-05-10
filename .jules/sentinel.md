## 2025-02-18 - Path Traversal Vulnerability in File Uploads
**Vulnerability:** The `save_upload` function in `apps/api/app/services/files.py` used `Path(filename).name` to extract the base name from user-provided filenames. On POSIX systems, `Path` does not strip backslashes (`\`), allowing an attacker to submit paths like `..\..\etc\passwd`, which would be appended to the storage path.
**Learning:** `Path.name` is insufficient for preventing path traversal when processing potentially malicious filenames from users, particularly cross-platform exploits using backslashes.
**Prevention:** Always normalize backslashes to forward slashes before parsing file paths, and apply a strict regex allowlist to sanitize the filename characters before writing to the filesystem.
