# Filesystem policy implementation — 2026-10-18

UL-082 is active. [Maintained source and contract](../../../experiments/filesystem-service/README.md)
implement the first private userland Rust policy layer over the pinned readonly
namespace design, with explicit WRITE attenuation, trusted policy UTC, shared
alias sizes, one provider call per context and irreversible-error retirement.
This is host policy execution and a no_std library build, not native C/IPC service
or persistent boot-to-shell acceptance. No sibling wire, fixture, pin or SDK changes.

[Inputs](inputs.json) match five current producer source hashes to the exact
native-pair source_freeze_base before adaptation. [Original paired receipt](producer-pair.json)
records one successful native overwrite/fresh readonly readback, earlier failures
and service-owner assignment. This review does not independently replay that native
pair. Prior creator timeouts in our older STATE are historical; they are not the
current next gate. [Planned and actual review](review.md) tracks the scope and gaps.

Thirteen host tests and eight compiling semantic-omission controls are selected.
Rust1.98.0, explicit2021 edition, warnings denied, unsafe forbidden, no_std library
with panic=abort, default Clippy on library and tests, rustfmt, actual Python3.10.21/
3.14.7 execution/syntax, local quality/all three published pins and whitespace
must pass before this slice completes. Compact per-attempt records retain exact
source/tool/argv/environment/deadline/output/cleanup identities. Generated builds
and mutated copies are disposable only after checked compact retention.

Success is scoped to authorization before provider effects, coherent size/EOF and
permanent retirement/no retry for uncertain or irreversible completion. No claims
of native authority enforcement, C borrow safety, cleanup quiescence, sustained
writes, resource/stack fit, general POSIX behavior or persistence follow here.

Next UL-082 work is the concrete private C bridge and matched transport/engine
consumer evidence. Aether owns missing original-engine mutations and sustained
transaction qualification; sys-init/pkg-mgr activation/install policy remains with
those owners. R1 requires the persistent filesystem-backed shell/runner/package
composition. No release, M3 or complete runtime story is closed by this slice.

Final result: [scoped summary](summary.json) and [retention/readback](retention.json).
All13 host tests and eight omission controls pass. The actual minimum/current
runs use identical maintained source and produce identical no_std library bytes.
Clippy library/tests, formatting, syntax, all published pins and whitespace pass.
Six generated roots are removed after366 compact records and exact historical
source/driver versions are retained. Existing quality-tool child receipts remain
compactly under its own ownership. No archive/VM/image was created here.
