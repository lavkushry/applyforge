## 2025-02-13 - Path Traversal via Unsanitized Backslashes
**Vulnerability:** Path traversal vulnerability when parsing user-uploaded filenames on POSIX systems.
**Learning:** `Path(filename).name` on POSIX systems treats backslashes (`\`) as valid filename characters, allowing attackers to upload files like `..\..\..\etc\passwd` which then get stored improperly and bypass intended filename extraction.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user input to `Path()` or use a dedicated sanitization function for untrusted filenames.
