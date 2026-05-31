## 2024-05-31 - Path Traversal in filename.name
**Vulnerability:** Path traversal vulnerability in Python using `Path(filename).name` on POSIX systems where user-uploaded filenames containing backslashes are not properly stripped of path structures.
**Learning:** Backslashes are not treated as valid directory separators on POSIX systems by `pathlib.Path`, making `Path("a\\b.txt").name` return `a\\b.txt` instead of `b.txt`.
**Prevention:** Always manually normalize backslashes to forward slashes (e.g., `filename.replace("\\", "/")`) before passing user input to `Path` on POSIX systems to ensure proper directory prefix stripping.
