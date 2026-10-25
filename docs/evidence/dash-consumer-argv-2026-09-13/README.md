# Unchanged DASH-argv producer qualification — 2026-09-13

Requirement: actual dash evaluates the unchanged userland argv.sh, launching its
unchanged helper body through real fork/exec/wait. Preserve four arguments,
WITNESS=value, quoted whitespace/literal wildcard, output `argv ok\n`, exit0,
CLOEXEC and six actual task reclaims across two lifetimes.

Forbidden: replacing helper with a builtin, losing an argument/environment value,
accepting missing helper execution, fabricated wait status, leaked descriptors,
ambient executable lookup or reusing child authority. Aether owns the bounded
adapter; userland retains SDK ownership and independent acceptance. No sibling
edits. The granted /inputs/helper name is an explicit image mapping, not path
lookup or a mounted filesystem.

Reuse the existing nonserial dash dispatch and three-stream backend. A separately
compiled role calls the already pinned helper after validated startup; unchanged
profiles retain their existing ELF bytes. No new dependency, ABI, quota, unsafe
boundary or service. Existing single-context buffer and frozen-child publication
obligations apply. This is simpler than adding another dispatcher; no existing
fixture can be removed before its consumers migrate. Current fixed workload
validation remains separate from future general shell policy.

Tests selected before implementation: focused positive plus argument corruption,
environment corruption and skipped-helper controls; complete connections suite,
host/harness/pin checks, scoped C/Rust formatting and simplicity hashes. Freeze
sources during runs and retain all attempts. Document exact source pins, limits,
commands and outcomes; update STATE and the existing native shell reference.

Status: bounded producer qualification passes. All 284 connections cases pass in
869.89s. Host tests (100 Python tests and Zig checks), scoped C/Rust formats,
workflow and immutable pins pass. The separate simplicity manifest and four files
match their adopted hashes. No released pin or sibling repository changed.

Final evidence retains 253 frozen runtime/test sources,
239 harness source hashes and 5066 target artifacts.
Both preflight directories are archived with their original source snapshots and
all archive members verified. Final sources stayed frozen across the successful
preflight, host checks and full native suite.

The first preflight passed the positive and observed the correct child91/owner2130
argument rejection, but the harness prepended an unrelated parent72 requirement.
The correction excludes only this new profile from that older shell rule. The
second preflight passes all four cases. No runtime change was needed after the
first attempt. Detailed receipts preserve both attempts; no failed run was erased.

All 95 prior copied-fork C ELFs, 23 prior replacement ELFs and older owner images
remain unchanged. New owner is9,336bytes (environment control9,416); the suite's
largest owner remains15,416 within the existing16,384 envelope. No capacity or
kernel change. The new helper role is appended without moving old image indices.

The [contract](../../NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-argv--2026-09-13)
defines exact authority, startup, cleanup and replay. Use the existing complete
connections command with the captured SDK and tool lock from connections.json.
`native-traces.json` records exact terminal/reclaim results. `sources.tar.gz` and
`implementation.diff` freeze the change relative to the preceding serial packet.

This is producer execution of DASH-argv, not independent acceptance or completion
of the twelve-workload dash gate. The next unchanged script is DASH-signal-table;
SDK integration, broader pipelines/recovery and filesystem/package/sys-init R1
assembly remain separately required.
