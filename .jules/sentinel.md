## 2024-07-17 - Fix path traversal in file uploads
**Vulnerability:** The file upload handler used `Path(filename).name` to sanitize the uploaded filename. This does not protect against malicious paths utilizing backslashes (`\`) or other techniques on all OS variants.
**Learning:** `pathlib.Path.name` is insufficient for securely sanitizing filenames provided by user uploads, especially cross-platform.
**Prevention:** Use a dedicated `secure_filename` function that aggressively strips directory traversal characters, normalizes path separators, and ensures only safe characters remain.
