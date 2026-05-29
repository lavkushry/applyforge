## 2024-05-29 - Path Traversal in File Uploads
**Vulnerability:** Path traversal in file uploads using `Path(filename).name`.
**Learning:** On POSIX systems, `Path(filename).name` does not treat backslashes as path separators, so `..\..\etc\passwd` is treated as a valid filename rather than traversing directories. This allows attackers to write files to arbitrary locations.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before parsing with `Path`.
