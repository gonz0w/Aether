# 0008: Test explicit-stop I/O closure with existing native inputs

Accepted 2026-09-05 for the BG-032/BG-040 experiment, following BG-055's frozen
native refresh. Aether owns the existing AENFD001 operations; userland owns its
unchanged descriptor probe. Only sys-init client policy and its harness change.
Shared pins and companion working trees remain untouched.

Launch the existing I/O worker, wait for historical readiness while checking it is
still live, and confirm both output streams are empty/open. Stop it before sending
input, so the probe cannot finish its normal input/output path first. Require stop
return 0, retained status 144 (detail 143 + 1), terminal kind 3 and historical
readiness 1. Repeated stop must preserve that terminal result. Both empty outputs
must now report EOF, and both byte submission and producer sealing must reject.

Reclaim explicitly; old status, stop, input, output and reclaim operations must
reject the stale handle. Launch a distinct next generation in the same slot.
Require its output streams to be open/empty rather than inheriting EOF, then run
the unchanged full input/backpressure/seal/normal-output fixture and reclaim it.
The profile's existing two-reclaim completion marker is preserved.

Use a separate client file and opt-in builder variants; existing supervision and
I/O client bytes retain their source paths/options. A wrong-stop-detail client
must reject semantically. Also rerun omitted-zeroing rejection and the original
I/O client against the same frozen kernel and SDK. Pin the SDK receipt/probe and
all consumed code, and retain exact markers, exits and artifact identities.

This witnesses stop of a live, ready worker with empty output and a clean next
generation. It does not witness retention of nonempty output across stop, a real
worker fault, graceful signal handling or owner recovery. Those need separately
specified probes; do not modify companion fixtures or invent fault operations to
make this test appear broader. BG-032/BG-040 retain those follow-ons.

## Result

The [four-case target suite](../evidence/native-io-stop-2026-09-05/README.md) passes, including wrong-detail and omitted-zeroing controls plus original-I/O compatibility. The new client is 1,678 bytes within the existing 4 KiB bound. All three legacy supervision variants remain byte-identical. Standard/host/model gates pass; source and artifact hashes are retained. No companion repository was changed.
