## 2024-05-24 - Path Traversal Vulnerability in File Uploads
**Vulnerability:** User-uploaded filenames were passed through `Path(filename).name` which does not strip backslash (`\`) directory separators on POSIX systems, potentially allowing path traversal attacks.
**Learning:** `pathlib.Path.name` uses the underlying OS's path separator logic. On Linux/macOS, `\` is treated as a valid filename character, so `foo\..\..\etc\passwd` becomes the literal filename instead of extracting `passwd`.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename.replace("\\", "/")`) and apply a regex allowlist before extracting the base name for any user-provided file paths.
