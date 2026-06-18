## 2024-05-30 - Fix Path Traversal in File Uploads
**Vulnerability:** Path traversal possible via backslashes in user-uploaded filenames on POSIX systems.
**Learning:** On POSIX, `Path(filename).name` does not strip backslashes as they are considered valid filename characters, allowing `..\..\etc\passwd` to bypass directory stripping.
**Prevention:** Always manually normalize backslashes to forward slashes (`filename = filename.replace("\\", "/")`) before parsing user-uploaded filenames with `Path`.
