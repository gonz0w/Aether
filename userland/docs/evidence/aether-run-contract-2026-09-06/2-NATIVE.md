# Independent native bytecount integration (UL-057)

Nine native cases pass with an independently authored finite runner, two-binding
libc adapter and the previously host-tested bytecount source. The command source
hash is unchanged from UL-056's 21 host/control outcomes. Its native ELF is 13,504
bytes; the normal runner is 12,440 bytes. Separate entry code installs the validated
bindings before calling bytecount_main. The adapter supplies initialized TLS and
no local file positions. This is actual Aether command execution through musl,
not host emulation or a hard-coded output/exit helper.

The source-rebuilt Aether broker/backend come from the completed
native-command-io-2026-09-05 archive. No sibling or shared transport source changed.
The new client channel object renames the original hook; native-io.c provides the
single active __aether_io. Both bootstrap entries validate before either goes live.
Parent bindings are 3/read and 4/read-write; child stdin/stdout are 0/read and 1/write.
File calls validate local binding/rights/count, issue at most one 16-byte transfer,
validate reply bounds/metadata/padding, then copy caller data. Close consumes the
local binding once. Transfer/malformed file-reply failure poisons the connection;
that mechanism still needs dedicated two-binding failure controls in UL-058.

The runner builds the candidate's 384-byte launch frame with two inheritance entries
and copied argv/env. It rejects unknown name, duplicate destination, widened rights,
wrong source, excessive argc, nonzero unused startup bytes and unsupported version,
then successfully launches. Every rejected launch sends a complete frame, so the
subsequent valid launch exercises alignment. The runner mutates its source buffer
after successful admission; bytecount validates argc, option and LC_ALL. This does
not independently check every startup string (notably argv[0]) or arbitrary mutation
schedules; expanded startup/partial-frame tests remain open.

The runner closes its input alias while the child retains stdin, collects actual
terminal detail/kind once, rejects a foreign and then consumed receipt, observes
output EOF at the shared position, and closes its output alias. The command closes
both standard bindings. Each successful scenario repeats for two fresh generations,
with terminal order command/runner/backend and six reclaims.

| Case | Required outcome |
| --- | --- |
| Nonempty input | Same command computes `6\n`; command 0, runner 29, backend 17 |
| Empty input | Same command computes `0\n`; same successful cleanup |
| Rejected native launch | Explicit EINVAL on first-round attempt; successful retry, both rounds |
| Partial reservation | Explicit EBUSY and rollback; successful retry, both rounds |
| One-byte writes | Command loops over short results and completes exact output |
| Full output | Command returns its real operational exit 1; runner collects 1; successful fixture cleanup |
| Wrong startup | Modified option produces command 64; runner assertion 53; broker 970/reclaimed 0 |
| Wrong reported status | Command actually exits 0; runner assertion 53; broker 970/reclaimed 0 |
| Skipped storage | Command exits 0 but owner output verification rejects at 985/reclaimed 0 |

Positive cases require the unchanged CONNECTIONS PASS marker and exact terminal
sequence; negative cases require exact command/runner/broker contexts with no
success marker. Timeouts, unrelated panics and build failures cannot pass. The
full-output case uses exit 1 from our command, rather than adapting it to the owner
command's private exit 82. The broker already retains actual status, so its source
needed no change.

Exact output and input preservation are checked by the owner broker's independent
backend readback. The userland runner sees EOF after child output because it shares
that position; it does not independently read `6\n` or `0\n` from the start. The
skip-write control exercises this explicit trusted verifier boundary. This resolves
the bounded witness honestly without pretending EOF is byte comparison or adding
a client-local seek.

```sh
python3 experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-command-io-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The pinned 178-file archive, producer summary/report and tested strict-musl/tool
inventory are checked before private builds. Archive links, traversal, duplicates
and unlisted files reject. Owner tools verify boot dependencies. Five independent
ELFs retain static x86-64/TLS/NX/W+X/dynamic/undefined/Linux-syscall checks and maps;
command maps explicitly require musl read/write/close and exclude threaded
cancellation. Source/SDK stability checks pass. Commands and versions retain
Clang/LLD 21.1.8, Rust 1.98.0, Zig 0.16.0 and QEMU 11.1.1. QEMU uses TCG, one CPU,
256 MiB, no NIC, private firmware variables and the pinned 30-second watchdog.

[Evidence](../../docs/evidence/native-command-userland-2026-09-05/README.md) retains
sources, archive, clients, brokers/backends and serial logs. Large generated images
remain in `build/native-command-userland-7qy90ndd` with receipt identities. All nine
cases passed on the first build/run. All three standards checks pass. Older profile
suites were not rerun because their implementation sources were unchanged; the
producer's broader regressions remain separate.

The finite runner intentionally retains the broker's required exit 29 and fixed
startup. It is not the public aether-run CLI, and this does not close full CR-01,
dash/M3 or POSIX spawn/wait. UL-058 adds two-binding bootstrap/unknown-delivery and
malformed-frame/abnormal-child coverage. UL-059 specifies public runner argv/status
integration: the current broker hard-codes parent startup and demands runner 29,
so public exit mappings need an explicit owner contract change. Package reconstruction,
sys-init policy, general FD operations, fork/exec/pipes/TTY and PD review remain open.
