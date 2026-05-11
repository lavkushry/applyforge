## 2024-05-11 - Path Traversal Vulnerability via Backslash
**Vulnerability:** Path traversal possible when using `Path(filename).name` on uploaded files.
**Learning:** Python's `pathlib.Path(filename).name` does not strip backslashes (`\`) on POSIX systems, meaning a malicious filename like `..\..\..\etc\passwd` would evaluate to the entire string instead of just `passwd`.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g. `filename.replace("\\", "/")`) before calling `Path().name` or extracting the base filename.
