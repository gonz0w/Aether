# UL-059 lost/partial reply contract

2026-09-07, before implementation. Selected AEOUT001 fixture only; no kernel,
capacity, dependency, released pin or sibling changes. Userland owns parsing and
independent adoption. Existing deterministic failure and child profiles remain.

The owner commits the first 16-byte write (stdout or stderr), or consumes stdout
close after full help delivery, then closes its actual reply endpoint after zero
or eight reply bytes. Client must observe EIO, poison the connection, never replay
or issue another channel call, attempt local consuming closes and exit1. Test-only
trap counters independently check no client traffic after incomplete receipt;
owner separately rejects all requests after cutting the reply channel.

The client cannot infer delivered bytes or remote alias cleanup. Only after exact
normal terminal status1, no partial/queued request and exact expected live aliases
may the owner retire its remaining aliases, read back both sinks/input, close all
backend handles with stale denial and reclaim parent/backend across two generations.
Expected live aliases at terminal: both after lost write; stderr only after lost
stdout-close reply. Require no alias remaining before backend cleanup. Owner proof
is not a client recovery assertion or a new reconciliation API.

Test zero/partial write replies, stderr reply loss, zero/partial close replies;
negative clients clear poison/send again or hide failure, and a broken owner skips
remaining-alias retirement. Require exact rejection, no generic watchdog success.
No new unsafe block; partial reply uses a synchronous trap with a bounded stack
slice and no retained pointer. Format Rust1.98.0 edition2024/C clang-format21;
legacy transport remains two-space style. Full command, inherited-launch and
connections suites plus host/Zig/pin/workflow/format checks. Freeze inputs, retain
all attempts, update NATIVE-COMMAND-IO/inventory/STATE. Pre-effect disconnection,
other reply cuts, owner/backend death and exact denied launch remain open coverage.
