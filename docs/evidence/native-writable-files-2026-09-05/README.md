# Bounded writable scratch witness

2026-09-05: five writable-file cases pass, including successful mutation and
specified corruption, truncated-frame, zeroing and write-rights controls. Three
read-only, five launch and four channel regressions pass. Host checks, 44 Python
tests and three pinned standards checks pass. Source and serial identities were
verified when retaining this evidence.

[Service contract and commands](../../NATIVE-FILES.md). Results retain source/tool
pins, commands, images, maps and logs; large artifacts remain at the private paths
in those reports. This extension modifies the Rust service, C test client and
shared test runner only. No kernel runtime, companion source or release pin changed.
Memory/descriptor/default-display target suites were not repeated. Scratch data
is volatile; no native shell, libc file adapter or package installation is claimed.
