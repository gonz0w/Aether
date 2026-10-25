# Native launch byte channel witness

2026-09-05: all four channel cases pass: normal producer termination, producer
fault, controlled stop, and rejection of a wrong-count consumer. Five existing
launch cases, eleven memory cases, twelve frozen userland consumer cases, kernel
host tests, 44 Python tests, three standards checks and default two-core/framebuffer
acceptance also pass. No companion source or pinned standard changed.

[Contract and reproduction](../../NATIVE-CHANNEL.md). Results and maps bind exact
sources/tools/images and logs. Large ELF/ISO artifacts remain in the private paths
recorded in commands. Source and serial digests were checked when retaining this
report. Existing userland tests consume their previous profile, not this new ABI.
No POSIX pipe/descriptor inheritance, process service or native shell is claimed.
