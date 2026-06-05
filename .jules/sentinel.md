## 2024-06-05 - Prevent Path Traversal by Normalizing Backslashes
**Vulnerability:** User-provided filenames containing backslashes (e.g., `..\..\..\etc\passwd`) were processed by `Path(filename).name` which failed to strip backslashes on POSIX systems, allowing path traversal.
**Learning:** `pathlib.Path(filename).name` behavior varies by OS. On POSIX, backslashes are treated as standard characters within a file name rather than directory separators, making them vulnerable to malicious payloads crafted to exploit this OS-level difference.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user-supplied filenames to `Path()`.
