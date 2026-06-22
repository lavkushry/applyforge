## 2024-05-18 - [Path Traversal in File Uploads]
**Vulnerability:** File upload endpoints using `Path(filename).name` do not strip backslashes correctly on POSIX systems, creating a path traversal vulnerability.
**Learning:** Python's `pathlib.Path` treats backslashes as valid filename characters on non-Windows platforms, meaning payloads like `..\..\..\etc\passwd` result in a filename of exactly that, allowing files to be written outside the intended directory.
**Prevention:** Explicitly sanitize filename inputs by normalizing backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing them to `Path`, ensuring that directories are correctly parsed and stripped by the `.name` attribute across all platforms.
