## 2024-05-24 - [Path Traversal bypass using backslashes]
**Vulnerability:** Path Traversal via uploaded filenames (using `..` or Windows backslash patterns on POSIX systems).
**Learning:** In Python (`apps/api`), `Path(filename).name` is insufficient against path traversal because it does not strip backslashes (`\`) on POSIX systems.
**Prevention:** Always manually normalize backslashes to forward slashes, and apply regex allowlists before extracting the base name.
