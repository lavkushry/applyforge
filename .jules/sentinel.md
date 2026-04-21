## 2025-02-25 - Path Traversal in File Uploads
**Vulnerability:** User uploaded filenames were being processed by `Path(filename).name` before being saved, allowing for Path Traversal attacks via backslashes (e.g., `..\..\..\etc\passwd`).
**Learning:** `Path(filename).name` does not strip backslashes (`\`) on POSIX systems, making it insufficient for sanitizing user-provided paths from non-POSIX systems like Windows.
**Prevention:** Always manually normalize backslashes to forward slashes before parsing with `Path` or apply a robust custom `secure_filename` function that strips backslashes, enforces an allowlist (alphanumeric, dots, underscores, dashes), and strips leading dots to prevent `..` sequences.
