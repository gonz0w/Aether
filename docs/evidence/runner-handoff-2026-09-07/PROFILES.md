# Selecting the candidate profiles

These are opt-in experiment selectors in the source snapshot, not new public APIs.
The source `scripts/launch_smoke.py --command-runner` records exact compiler/linker
commands in its receipt and generated text/carrier inputs in the artifact archive.
Replace consumer clients only in an independently rebuilt consumer experiment;
do not treat producer ELF execution as consumer acceptance.

| Selected experiment | Owner rustc cfg | Parent fixture defines | Backend cfg | Boot oracle |
| --- | --- | --- | --- | --- |
| Help0 | runner_streams | RUNNER_STREAMS, STREAM_FD=1, STREAM_STATUS=0; generated help text | runner_streams | native-runner-local=true; four reclaims |
| Version0 | runner_streams, stream_version | As help, generated version text | runner_streams | local/four |
| Usage64 | runner_streams, stream_usage | RUNNER_STREAMS, STREAM_FD=2, STREAM_STATUS=64; usage text | runner_streams | local/four |
| ENOENT2 | runner_streams, runner_denial, denial_missing | RUNNER_STREAMS, RUNNER_DENIAL, DENIAL_ERRNO=2, STREAM_FD=2, STREAM_STATUS=2; unavailable text | runner_streams, runner_denial | local/four |
| EACCES2 / EBUSY2 | Above, denial_rights / denial_busy | DENIAL_ERRNO=13 /16; denied/capacity text | combined backend as above | local/four |
| Normal child0 | runner_success | RUNNER_STREAMS, RUNNER_SUCCESS, success-client.c | combined backend as above | default/six |
| Child normal134 / fault134 | runner_success, success_nonzero / success_fault | Same parent; child CHILD_STATUS=134 / CHILD_FAULT | combined backend | default/six |
| Logical startup forwarding | runner_success, runner_startup; success_wide and/or success_fault where selected | RUNNER_STARTUP, RUNNER_FORWARD, FORWARD_FIRST=1/2; WIDE_STARTUP for six strings; child FORWARD_OBSERVER | combined backend | default/six |

The full receipt is authoritative for flags, images, loader envelope, native entropy,
SDK paths/hashes and configured controls; this table is navigation, not a replacement
build recipe. Selected failure cfgs are listed per case in that receipt.

AEOUT001 carries stdout/write512 and stderr/write256. AERIO001 carries those plus
child-input/read6 and child-output/read-write64. Each has a32-byte header and ordered
32-byte records with generation/refs/rights/capacity/reserved validation. See the
snapshot's docs/NATIVE-COMMAND-IO.md for exact bytes. AERUN001 is a separately
selected224-byte logical-argument carrier preceding the bindings. It does not widen
kernel argv. Startup rejection110 and operational1 are fixture outcomes; do not
turn incomplete admission/collection into successful local actions.

Local owner: user/native-command/streams.rs; successful-child owner: success.rs;
common validate/admit: owner.rs; independent backend: user/native-files/streams.rs.
All are user-space conformance components trusted for their validation assertions.
Kernel enforcement and per-core state ownership remain unchanged. The actual parser,
frontend, SDK closure, packaging and consumer pin belong to their respective owners.
