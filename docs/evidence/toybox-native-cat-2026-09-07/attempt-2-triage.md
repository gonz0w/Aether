# Attempt 2 — observation hook mismatch

Actual native copy terminated120 and owner1501 rejected; this is a failed positive,
not a passing negative. The retained xwrap object imports fflush/ferror, while
linked disassembly labels their shared addresses fflush_unlocked/ferror_unlocked.
Wrapping the disassembly alias therefore did not observe the real calls. Correct
wrappers to the actual undefined relocation symbols; keep upstream calls intact.
The original pre-code reference to unlocked names reflected that alias confusion.
No kernel, applet or stdio behavior is weakened; all affected cases must rerun.
