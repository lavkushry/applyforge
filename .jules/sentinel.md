## 2024-05-18 - Prevent Path Traversal in File Uploads
**Vulnerability:** The `save_upload` method in `apps/api/app/services/files.py` concatenated a UUID and the original filename. This allowed an attacker to inject directory traversal characters (e.g. `../`) and save the file in an unintended location by uploading a file named, say, `../../../etc/passwd`.
**Learning:** Even when appending random tokens to filenames, the original filename suffix must be sanitized so path traversal characters cannot escape the designated storage directory.
**Prevention:** Added a `secure_filename` function using regex substitution to strip out unwanted traversal characters and restrict characters to alphanumerics, dots, dashes, and underscores.
