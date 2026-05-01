## 2025-05-01 - Path Traversal Vulnerability on POSIX Systems via Path(filename).name
**Vulnerability:** Path traversal possible through malicious file uploads.
**Learning:** In `apps/api/app/services/files.py`, `Path(filename).name` was used to extract the file name from uploaded files. On POSIX systems, this behaves insecurely when a user inputs a filename with backslashes like `..\..\etc\passwd`, since POSIX does not treat `\` as a path separator, returning the full string.
**Prevention:** Use a dedicated `secure_filename` function that actively replaces backslashes with forward slashes (`/`), extracts the filename, strips leading dots, and aggressively filters invalid characters using a regex allowlist.
