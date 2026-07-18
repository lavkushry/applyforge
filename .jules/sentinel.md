## 2025-02-18 - Fix Path Traversal in File Upload
**Vulnerability:** File upload path traversal vulnerability due to relying on `Path(filename).name` which doesn't correctly parse Windows paths containing `\` on Linux.
**Learning:** Using Python's `pathlib` for sanitization is OS-dependent. On Linux, a Windows path like `C:\path\to\evil.txt` is interpreted as a single filename, preserving the backslashes and bypassing intended directory boundaries.
**Prevention:** Always normalize both `\` and `/` to a unified separator before extracting filenames, and use an allowlist approach for valid characters.
