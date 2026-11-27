# Failures and Diagnostic Log (FAILURES.md)

**Rule Reference:** Non-Negotiable Operating Rule R3 ("NO SILENT EXCEPTIONS. If something fails, log it in docs/FAILURES.md with the full error and your diagnosis, then fix the root cause or stop and report.").

---

### [F01] Git Ref Lock Permission Denied in Windows Standard Sandbox Mode
- **Date/Time:** 2026-11-27 17:35:54
- **Command:** `git checkout -b phase-0-audit-setup` (Standard Sandbox Mode: `BypassSandbox: false`)
- **Full Error Output:**
  ```text
  fatal: cannot lock ref 'refs/heads/phase-0-audit-setup': Unable to create 'E:/Software/Fake-news-detector/.git/refs/heads/phase-0-audit-setup.lock': Permission denied
  ```
- **Diagnosis:**
  Under Windows standard sandbox mode, filesystem write isolation restricts modifications to hidden directories (such as `.git/refs/heads/`). Read-only operations (`git status`, `git log`) execute without error, but ref locking and branch creation fail on OS-level file lock acquisition.
- **Root Cause Remediation:**
  Executed the git checkout branch creation command with `BypassSandbox: true`, which successfully acquired the lock and created branch `phase-0-audit-setup`. Subsequent read commands will remain sandboxed, while git commit / branch operations modifying `.git` will use BypassSandbox as permitted by terminal sandbox rules.

---

### [F02] pyreadline3 Console Deletion WinError 0xc0000008 on Pytest Teardown
- **Date/Time:** 2026-11-27 17:34:55
- **Command:** `python -m pytest tests -v`
- **Full Error Output:**
  ```text
  Exception ignored in: <function Console.__del__ at 0x0000025CE71D82C0>
  Traceback (most recent call last):
    File "C:\Users\DHRUV\AppData\Local\Programs\Python\Python312\Lib\site-packages\pyreadline3\console\console.py", line 256, in __del__
  OSError: [WinError -1073741816] Windows Error 0xc0000008
  ```
- **Diagnosis:**
  `pyreadline3` attempts to free Windows console handles during interpreter exit. On Windows PowerShell running in automated subshells, the handle is closed before the garbage collector invokes `Console.__del__`.
- **Root Cause Remediation:**
  This is an ignored Python interpreter teardown exception in an optional interactive CLI library (`pyreadline3`). Pytest exited with code 0 and all 38 tests passed. No code changes needed; documented for full transparency.
