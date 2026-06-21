## 2024-06-21 - Path Traversal via Backslashes on POSIX
**Vulnerability:** User-uploaded filenames were passed directly to `Path(filename).name` without checking for backslashes.
**Learning:** POSIX paths treat backslashes as regular characters. An attacker could upload a file with backslashes to bypass filename sanitization checks.
**Prevention:** Always normalize backslashes to forward slashes before parsing filenames with pathlib on potentially POSIX-based servers.
