# Scratch descriptor adapter and gateway — 2026-09-14

[Pre-code review](../../NATIVE-SHELL-STARTUP.md#scratch-descriptor-adapter-and-owner-gateway)
defines the grant, request/reply shape, ownership, errors and test scope. New C
scratch-client.h implements private open/open64 using existing descriptor arrays
and mask guards. New Rust Owner gateway validates authenticated peer selection,
root, binding and canonical records, then calls existing description operations.
Neither is newly wired to an application-facing native profile in this packet.

The C host witness passes grant/epoch validation, read/write and CLOEXEC flags,
FD/binding exhaustion before transport, canonical denial, malformed/unknown replies,
live-binding preservation, transport failure poisoning and no replay. Two isolated
mutants drop CLOEXEC or allow installing over a live binding. Each compiles and
fails its exact CHECK expression with exit90; no crash/timeout is counted as success.

Owner/backend composition passes15 Rust tests (nine owner/gateway plus six backend).
Gateway tests check root and binding enforcement, canonical rejection, real scratch
write/reopen/read and absence of authority for an unadmitted peer. The full host
suite passes104 Python tests and all three offline standards checks. Formatting,
workflow and the four-file simplicity snapshot verify. No unexpected failure.

C compiles with pinned Clang21.1.8 against the native SDK headers; the owner also
passes the existing no_std compilation check. These are compilation/host results,
not Aether execution. The host C witness uses host libc constants and a deterministic
transport, separately from Rust backend composition; it is not an end-to-end native
wire test. No actual dash, dup/CLOEXEC across exec or frozen FD-table acceptance.
Prior328-case target evidence retains its original source scope; source-delta.json
records affected old inputs. No public API or SDK installation was performed.

The header explicitly forbids combining old file/pipe/null bindings. Application
integration must emit/consume AESFD001, enable five scratch bindings, route requests
through the gateway and validate fork/exec snapshots. Only the final local alias
may release the owner holder. Poisoned-process stop/reclaim is still required.
No allocator, kernel ABI, shared mutable byte store or dependency was introduced.
BSD-2-Clause applies to new original code. Siblings and released pins are unchanged.

Exact implementation/test/docs are in sources; checks and raw logs are retained.
artifacts.tar.gz contains mutated headers/witnesses, test binaries and native C
object. Every member was read back and compared before deleting only its generated
duplicate directory. The retained runner documents original commands; fresh runs
must not overwrite this sealed packet. Use the documented test-discovery command.
