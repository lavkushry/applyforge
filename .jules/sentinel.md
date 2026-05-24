## 2024-11-28 - Path Traversal in File Uploads
**Vulnerability:** Unsanitized backslashes (`\`) in uploaded filenames allow path traversal on POSIX systems (e.g. `../../../etc/passwd` using backslashes) because `Path(filename).name` does not strip backslashes on non-Windows systems.
**Learning:** `pathlib.Path(filename).name` only handles the path separator for the current OS. On POSIX systems, `\` is treated as a valid filename character, not a directory separator, leading to unexpected path resolution if the filename contains backslashes injected by a malicious user.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename.replace("\\", "/")`) before passing user-provided filenames to `pathlib.Path`.
