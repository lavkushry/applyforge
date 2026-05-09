## 2024-03-24 - Path Traversal via Backslash Injection on POSIX

**Vulnerability:** Path traversal and arbitrary file write risk when saving user-uploaded files due to reliance on `Path(filename).name` for sanitization.
**Learning:** On POSIX systems (like Linux and macOS), Python's `pathlib.Path` treats backslashes (`\`) as regular characters in filenames, not directory separators. A malicious payload like `..\..\..\etc\passwd` or `foo\bar\baz.txt` is treated as a single filename. `Path(filename).name` will not strip the `foo\bar\` prefix, allowing the full malicious path string to be appended to the target directory.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before extracting the base name. Additionally, apply a strict regex allowlist (e.g., `re.sub(r'[^a-zA-Z0-9.\-_]', '_', base_name)`) to ensure no unexpected characters can influence the final file path.
