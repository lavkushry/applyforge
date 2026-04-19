## 2024-05-24 - Path Traversal in File Uploads
**Vulnerability:** Path traversal in file uploads (saving files via `Path(filename).name`).
**Learning:** In POSIX environments, `Path(filename).name` doesn't filter out backslashes (`\`). A user uploading a file named `..\..\etc\passwd` would trick the application into traversing directories and storing the file or overwriting files outside the intended storage location on Linux/macOS environments.
**Prevention:** Avoid relying solely on `Path(filename).name`. Normalize backslashes to forward slashes first (`filename.replace('\\', '/')`) and sanitize by stripping leading dots and dropping non-alphanumeric characters, as implemented in `secure_filename`.
