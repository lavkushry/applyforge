## 2024-05-09 - [Path Traversal in Python Pathlib]
**Vulnerability:** Path traversal vulnerability in `apps/api/app/services/files.py` due to using `Path(filename).name` on raw user input.
**Learning:** Python's `pathlib.Path.name` does not strip backslashes (`\`) on POSIX systems, allowing attackers to bypass extraction and execute path traversal attacks (e.g., `..\..\etc\passwd`).
**Prevention:** Always manually replace backslashes with forward slashes (`filename.replace("\\", "/")`) before extracting the base name, and apply a strict regex allowlist to the resulting filename.
