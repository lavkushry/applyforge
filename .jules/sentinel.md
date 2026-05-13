## 2025-02-15 - POSIX Pathname Traversal Vulnerability

**Vulnerability:** A path traversal vulnerability existed in file uploads. The `save_upload` function relied on `Path(filename).name` to extract the base name of a user-provided filename. On POSIX systems, `Path` does not recognize backslashes (`\`) as directory separators, meaning a filename like `..\..\..\etc\passwd` would be treated as a raw filename rather than a path, and appended to the storage path, allowing files to be written outside the intended directory.

**Learning:** `Path(filename).name` is insufficient for preventing path traversal when the input originates from untrusted sources, especially on POSIX environments where backslashes are not automatically stripped by `pathlib`.

**Prevention:** Always manually normalize path separators (e.g., `filename.replace("\\", "/")`) before passing untrusted filenames to `Path`. Additionally, apply a strict regex allowlist to filter out unexpected characters and ensure a safe filename before saving.
