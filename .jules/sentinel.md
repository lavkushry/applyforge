## 2024-05-15 - Path Traversal in File Uploads
**Vulnerability:** User-uploaded filenames were passed directly to `Path(filename).name` in `save_upload`, which does not strip backslashes (`\`) on POSIX systems, allowing path traversal attacks via filenames like `..\..\etc\passwd` or arbitrary directory navigation during file creation.
**Learning:** `Path.name` is insufficient for preventing path traversal attacks against user-provided filenames across different operating systems.
**Prevention:** Implement a `secure_filename` function that explicitly replaces backslashes with forward slashes, strips leading dots, and strictly allowlists characters via regex before extracting the base name.
