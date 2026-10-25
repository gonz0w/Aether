# Signal CPU frame implementation

Requirement, recorded before code: implement the allocation-free CPU-state codec
needed by the proposed one-context shell signal return. Aether owns validation;
userland still owns libc translation and consumer acceptance. No syscall or
handler setter is enabled in this slice. No sibling or released pin changes.

Allowed: a fixed private experimental frame representation, checked stack
geometry, and structural CPU decoding into a candidate value. Forbidden: applying
unvalidated user mappings, trusting user selectors/privileged flags/MXCSR masks,
changing FS/TLS/authority, or creating an active-handler slot that longjmp leaks.
The caller must snapshot all input bytes and revalidate mappings under local
serialization before any future commit to Execution. CPU decoding alone does not
establish memory validity or authorize FXRSTOR/IRET.

Simpler alternative: put all checks in syscall dispatch. Separate the cohesive
CPU codec so malformed state can be tested without executing privileged restore;
keep copy/mapping and publication with the eventual runtime owner. No service,
profile, quota or generic serializer is introduced. No existing complexity is
removed yet: the C disposition table still has consumers and delivery is absent.

Selected checks: direct Zig codec tests in Debug and ReleaseSafe, malformed-field
and boundary matrices, deliberate privilege/FP-validation mutants, and the
existing full host test command. No target paths change, so QEMU entry/return,
real musl restorer, mapping-race/permission checks, FP execution and nonlocal exit
remain pending. Update the existing shell reference and STATE with this scope.

Results: four codec tests pass in Debug and ReleaseSafe (debug.log and
release-safe.log). The flags and MXCSR bypass mutants each exit 1 with
TestExpectedError in the corresponding validation test; complete sources and
outputs are retained under mutants/. These are deliberate negative controls,
not runtime failures. host.log records the passing full host command, including
98 Python tests and existing Zig/workflow/pin checks. No native execution was
performed; this test-only imported codec does not change runtime behavior.

Commands from the repository root:

```sh
zig test kernel/arch/x86_64/native_signal.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_signal.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

For each retained mutant, run the first command with its native_signal.zig path;
the required result is TestExpectedError in the named validation test, not a build
failure. The immutable review inputs from the previous step are unchanged.
