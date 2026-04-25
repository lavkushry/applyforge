## 2024-05-18 - Path Traversal Vulnerability on POSIX Systems via Path(filename).name
**Vulnerability:** Path traversal vulnerability in `apps/api/app/services/files.py` where `Path(filename).name` was used to safely extract the base name of uploaded files.
**Learning:** On POSIX systems (like Linux), the `pathlib.Path` module does not strip backslash (`\`) characters. If an attacker submits a filename like `..\..\..\etc\passwd` or `..\..\evil.pdf`, `Path(filename).name` returns the whole string unchanged, leading to a path traversal vulnerability.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) and apply regex allowlists before extracting the base name using `Path` to ensure secure filename generation.
