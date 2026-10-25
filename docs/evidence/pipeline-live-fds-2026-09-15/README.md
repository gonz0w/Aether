# Live libc fork/exec snapshots — 2026-09-15

The new parent captures its actual shared startup_fds table inside the public-fork
staging hook, instead of constructing a fixed snapshot in the test loop. Before
successive forks it creates CLOEXEC aliases at FD10/11/12 using fcntl. Parent and
child verify flags, close their own alias and check EBADF without losing the live
pipe holder. Child uses F_SETFD on unused ends, serializes that live table under
the startup mask and freezes for replacement. The source starts with four fixed
owner-granted pipe ends and no fabricated standard descriptors.

The owner derives bounded alias counts, rejects standard bindings that were never
granted, and uses the existing shared descriptor validator and both objects' live
holder checks before native copy. Exec validates the role-specific snapshot and
commits from its captured counts. Three lifetimes require nine public forks,
nine replacements, exact ten-byte data/EOF per pipe and fifteen normal reclaims.
The libc replacement continues to use actual dup2/fcntl/read/write/close.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes27 native cases on277 frozen inputs. Target case total is
72.957 seconds. The new pipe-exec-live-bad control rewrites the Second
writer's captured binding as another First writer; actual live-holder validation
rejects owner2731 before native copy/reclaim. Existing25 cases retain their exact
outcomes. No failed attempts occurred; intentional rejection evidence is retained.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0, with104 host checks in host.log. Final checks cover Rust1.98 edition2024,
Clang-format21.1.8 for the new/touched C, workflow/standards/experience, simplicity
manifest/four members, whitespace and frozen sources. The shared adapter and
upstream fork/rebind implementations are unchanged; their earlier legacy evidence
is retained, while full matching suites remain a handoff requirement.

## Compatibility and limits

compatibility.json compares 33 previous top-level ELF/raw images, with
25 byte-identical. New positive owner12432 bytes fits16384. Only private capacity
client/staging/owner/harness inputs change; no kernel, shared adapter, SDK,
dependency version, resource limit, sibling repository or released pin change.
Buffers stay live through masked synchronous capture/send. Authenticated channel
identity and live-holder validation remain independent of numeric descriptor data.
No extra alias-authority ledger or new unsafe boundary is introduced.

The unchanged consumer pipeline uses printf and two copy helpers; early-reader
requires pipefail and status42. Neither script is executed by this witness.
Initial pipe creation and exec scheduling are still fixed owner orchestration;
dynamic pipe/close/wait requests, actual dash, SIGPIPE/status composition, further
interruptions, matching full suites and independent intake remain next. Persistent
storage, packages and sys-init assembly remain R1 work. No full-shell/release claim.

The preimplementation review is in NATIVE-SHELL-STARTUP. Runtime and review-input
archives preserve sources and local guidance/test support. Target reports bind
commands, pinned tool/SDK identity, timestamps, envelopes/ISOs and serial hashes.
collect.py verifies all generated files against an archive before deleting only
this run's private output root; cleanup.json records it. Prior sealed packets are
unchanged. SHA256SUMS covers this packet except itself.
