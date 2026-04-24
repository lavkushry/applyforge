## 2024-05-18 - Path traversal via backslashes in user-uploaded filenames

**Vulnerability:**
A path traversal vulnerability was found in the file upload service (`apps/api/app/services/files.py`) where `Path(filename).name` was used to extract the safe filename.

**Learning:**
On POSIX systems, Python's `pathlib.Path.name` does not treat backslashes (`\`) as directory separators. Consequently, a malicious user could upload a file named `..\..\etc\passwd` or `foo\bar\..\..\baz.txt`, and `Path(filename).name` would fail to strip the traversal sequences, allowing attackers to write files outside the intended storage directory.

**Prevention:**
Always implement a custom `secure_filename` function that manually normalizes backslashes to forward slashes (`filename.replace("\\", "/")`) and uses a strict regex allowlist to sanitize characters before relying on path extraction tools. Additionally, strip leading dots to prevent hidden files or `..` sequences.
