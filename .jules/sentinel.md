## 2024-05-20 - Fix Path Traversal Vulnerability with Backslashes on POSIX

**Vulnerability:** Filenames uploaded by users on Windows systems might contain backslashes (`\`). When `Path(filename).name` from `pathlib` is used on POSIX systems, it does not treat backslashes as path separators. This leads to the entire string, including directory traversal characters like `..\`, being considered the file name. For example, `Path("..\\..\\etc\\passwd").name` evaluates to `..\\..\\etc\\passwd` instead of `passwd`. This creates a path traversal vulnerability.

**Learning:** `pathlib.Path` is platform-dependent. On POSIX systems, it maps to `PosixPath` which only splits paths using the forward slash (`/`). It ignores backslashes, making it inadequate for securely parsing untrusted filenames coming from different operating systems (like Windows).

**Prevention:** Before passing user-provided filenames to `Path`, explicitly normalize backslashes to forward slashes: `filename = filename.replace("\\", "/")`. This ensures consistent and safe path resolution regardless of the operating system where the application is hosted.
