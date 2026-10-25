# Client pipe creation and child collection — 2026-09-15

The private libc parent now receives an explicit two-object factory grant and
requests both pipes. It validates the full replies before publishing the lowest
free descriptors, then relocates the ends into FD3–6 using fcntl/close. No standard
streams are fabricated. A third creation returns ENFILE without modifying its
output pair. Existing live snapshots stage three public forks and distinct libc
replacement images. Parent closes its four ends through the shared facade; the
owner services those exact close requests before the existing data dispatcher.

After the pipeline completes, archive-derived public musl waitpid calls a private
request hook. The authenticated parent's child PID maps to its generation-bound
native handle. The owner derives status from the retained terminal record and
allows each child to be collected once. Repeat collection returns ECHILD and leaves
the client's status buffer unchanged. The normal lifecycle loop still verifies
and reclaims every native handle. Three generations require nine forks/replacements,
exact ten-byte data/EOF per pipe and fifteen normal reclaims.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes29 native cases on278 frozen inputs. Target case total is77.616 seconds.
The false-status control changes the third collected status: the parent rejects
with121, then owner2730 with zero reclaims. This verifies the public wait macro
check independently of the owner's normal status checks. All27 earlier cases
retain their expected outcomes. No failed attempts occurred; intentional rejection
logs are preserved.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0 with104 host checks. Final checks cover Rust1.98 edition2024,
Clang-format21.1.8, workflow/standards/experience, simplicity manifest/four members,
whitespace and unchanged frozen sources. The verified musl archive, extracted
waitpid/fork sources, upstream copyright and exact private compilation commands
are identified in the target report and archived artifacts. The SDK is unchanged.

## Compatibility and limits

All37 earlier top-level ELF/raw images are byte-identical (compatibility.json).
New positive owner13072 bytes and negative owner13088 fit16384. Kernel mapping
remains8007680 bytes. Changes are confined to six private capacity source/harness
files (source-changes.json), including one new header. No kernel, shared adapter,
SDK, dependency version, quota, sibling repository or released pin change.

Creation, exec and collection remain fixed owner phases. This is a bounded pipe
shim and private musl waitpid substitution, not general libc blocking/cancellation
support. Wait exchange runs in the single parent context; asynchronous callbacks,
nonzero exit/signal statuses and wait-any are not qualified here. The owner still
chooses object slots and schedules replacement. Numeric PID/reference data alone
does not confer authority; authenticated channels and exact native handles do.
The existing shared pipe/descriptor logic remains the only holder authority.

Actual dash orchestration, unchanged pipeline/early-reader scripts, SIGPIPE/status
composition, further interruption schedules, full matching connections/runner and
independent SDK/userland intake remain open. Persistent storage/OpenZFS, packages,
recovery and sys-init assembly remain R1 work. No full-dash or release claim.

The preimplementation review and outcome are in NATIVE-SHELL-STARTUP. Runtime and
review archives preserve source and local guidance/test support. Target results
bind tool/SDK identity, exact commands, timestamps, envelopes/ISOs and serial hashes.
collect.py verifies every generated file against its archive before deleting only
this run's private output root; cleanup.json records it. Existing sealed packets
remain untouched. SHA256SUMS covers all packet files except itself.
