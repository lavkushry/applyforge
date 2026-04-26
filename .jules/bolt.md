## 2025-02-28 - Avoid AI tool execution artifacts in git commits

**Learning:** When using scratchpad scripts to perform code transformations (e.g. `patch_roles.py`) they can accidentally pollute the working directory and be included in pull requests if not explicitly cleaned up.

**Action:** Always verify `git status` or remove temporary scripts using `rm` after they have been successfully executed to prevent repository pollution.
