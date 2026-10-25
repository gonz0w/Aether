# Bounded default dispositions and delivery-boundary review

Before implementation: enumerate default effects for the existing 1–31 signal
component and discard default-ignored occurrences on post and disposition change.
Do not enable native delivery, change the startup facade, allocate a syscall or
reinterpret exit/fault records. Unsupported stop/continue must remain explicit.

Use the existing domain-owned table and bitset; no extra state, service or flag
framework is needed. Retain checked selection/commit and peer/reset tests. Add
coverage for every supported default, queued-to-default-ignore transitions and
handler replacement. Select Debug/ReleaseSafe component tests, an ignore-discard
mutation and all host/pin checks. Native code is not imported by this component's
host-only consumer; no target conformance is claimed. This continues the existing
handler review and SE-01–05 assessment: retaining undifferentiated defaults is
simpler but insufficient for delivery; no compatibility path can yet be removed.

Results: seven owner tests plus nine frame tests pass in Debug and ReleaseSafe.
The initial enum label `resume` was reserved Zig syntax; its exact source and
failed compiler logs are retained. The corrected label is `continue_execution`.
The mutation removes queued-discard on installation; the named transition test
rejects the retained occurrence. Host/pin checks pass (98 Python tests).

The boundary plan in NATIVE-SHELL-STARTUP records raw/public flag differences,
query-state/range compatibility gaps and complete I/O guard scopes. No runtime
guard, syscall, signal terminal encoding, stop/continue or native delivery is
implemented here. No native regression is claimed for a host-only imported file.
The current C disposition table and all sibling repositories remain unchanged.

Reproduce from repository root:

```sh
zig test kernel/arch/x86_64/native_pending.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_pending.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The archived mutant must fail `default ignore drops queued occurrences without
dropping another signal` (and the pre-existing explicit-IGNORE test). Run its
`zig test zig-out/signal-defaults-mutant/native_pending.zig` after restoring the
archived paths to reproduce. `collect.py` verifies source archives, the preceding
packet and simplicity snapshot; manifest.json seals the retained evidence.
