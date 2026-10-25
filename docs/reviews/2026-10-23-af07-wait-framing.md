# ABI31 wait-record framing after complete native capture

Requirement: fix the producer boundary that caused AF07 native wait qualification
to reject a complete execution; preserve strict wait oracles, original failures,
old profile bytes, authority and current limits. No automatic native retry.

Approved attempt2 stops at `guarded duplicate park`; pristine reader passes,
writer helper7/parent0/engine0/21 cleanup/halt1975, both VM stops confirmed, no
recovery. Complete33818-byte non-clock transcript contains all eight excluded
parent wake records appended to application text: four getcwd ENOSYS diagnostic
fragments and four `$ ` prompts. They account for all eight missing column-zero
wakes in this attempt. The code writes bounded console bytes and kernel diagnostic
rows on the same UART without forcing a new line. The complete capture establishes
record interleaving in attempt2, not lost kernel completion. Attempt1's incomplete
capture remains historical and cannot be independently reconstructed.

Implement the smallest producer fix: only combined_owner_stack/ABI31, when wait
trace is enabled, write a newline before the existing exact wait record. Existing
row fields/status/identities/park-wake semantics and every old selection remain
unchanged. The native profile is BSP-only, IF=0 serializes the existing bounded
UART writes. No new state, grant, API, unsafe site, framing parser, service or global
log framework. UART failure remains bounded and must still reject qualification.
Application stderr may be split by diagnostic lines in this explicit trace profile;
this is not production terminal/rendering conformance or a fabricated getcwd fix.

Simpler alternative: reinterpret prompt/stderr-prefixed rows in the host checker.
Rejected: special-casing this transcript would couple qualification to shell text
and create a weaker provenance boundary. A producer-owned line boundary keeps the
strict existing parser and permits no user-output suffix promotion. One newline
per selected wait record is bounded by the unchanged retained64KiB capture; excess
still rejects, with no capture/time/resource increase or automatic growth.

Tests before freezing: compile the actual producer function with captured serial
writes for selected, old and disabled profiles, diverse partial console prefixes,
all roles/phases/error status. Compiling newline omission must fail; no source-text
assertion stands in for behavior. Replay full attempt2 through the unmodified
strict parser must still reject; diagnostic-only splitting of exactly those eight
complete suffix rows must account for116/116 parent waits and all other oracles,
without marking the failed native sequence accepted or inventing recovery.

Rebuild fresh engine/activation/guarded inputs and selected kernels after source
change, preserving old seals/released pins. Same code49152,stack/data8192,35MiB,
seven domains/twelve channels,writer60s6000/readers30s3000,64KiB and fixed script;
existing9/96 storage qualification remains separate. Actual owner size/stack and
source/tool/artifact intake still gate qualification. Retain compact failure and
new input hashes, remove owned generated outputs. Fresh human disposition before
another sequence; stop first unexpected result, no retry/recovery on failure.

The real getcwd ENOSYS diagnostic is a remaining R1 shell/filesystem integration
gap, not a logger defect or successful emulation. Keep it visible in STATE and
address through userland pathname/CWD policy when public filesystem bindings land.

Line framing is not authentication. Qualification still relies on the exact frozen
source/images and fixed input; arbitrary application output is not evidence of
kernel authority. This change adds no general untrusted-console log acceptance.

Results:39 focused methods pass (five actual kernel/entry, nine owner/capture,
25 AF07/intake/workflow). Scoped Zig format, component static/quality, experience,
standards and workflow checks pass. The actual producer newline omission compiles
and fails the independent column-zero assertion. Full attempt2 host projection
accounts for220/220; the actual failed capture still rejects. No broad suite rerun
or native acceptance. Fresh engine v7/activation v3/guarded v2 compile and pass
intake; owner/shell/helper/envelope bytes reproduce, selected kernel hash changes
for framing only. Owner39376/49152, resident7504/8192 and stack8000/8184 remain.
The new two images and final573-path/parser/reader-dependency/ISO freeze pass;
[current receipt](../evidence/af07-owner-native-2026-10-23/framing-prepared.json)
binds the pending sequence. All failed attempts remain compactly preserved.
No new VM runs after the producer fix. Fresh human disposition is the remaining
execution gate; no resource limit was raised and no sibling was modified.
