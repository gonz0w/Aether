# UL-062 pinned ASan host diagnosis — 2026-09-07

Pinned Homebrew Clang 21.1.8 ASan empty main does not start on macOS 27.0. A
live sample of the hung process shows AsanInitInternal → InitializeShadowMemory
→ get_dyld_hdr → malloc → AsanInitFromRtl → LockSlow. Stderr is empty. The
same empty main with pinned UBSan exits 0. A pinned ASan heap-buffer canary
also times out without AddressSanitizer diagnostics, so PXE-04 stays blocked.

Apple clang 21.0.0 ASan empty main exits 0 in this environment. That comparison
is recorded and is not a pin substitute; parser sources were not built with it.
No production parser, adapter, process helper, sibling repository or release
pin changed. Python 3.14.7 and 3.10.21 diagnosis runs pass.

Host UBSan plus existing native denial/reclaim witnesses remain compensation,
not a memory-safety proof. Independent review is pending. This does not close
UL-062.

See [PLAN.md](PLAN.md). Command: `python3 -B experiments/command-runner/check-asan-host.py`.

| Attempt | Result |
| --- | --- |
| asan-host-_e066cbn | Python 3.14.7: pass |
| asan-host-qrxa6u10 | Python 3.10.21: pass |
