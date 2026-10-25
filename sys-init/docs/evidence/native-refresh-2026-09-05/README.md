# Native integration refresh — BG-055

All five AENSUP01 supervision cases and four AENFD001 I/O cases pass against one frozen current-source checkpoint. [Summary](summary.json) records versions, settings and scope. No working kernel/userland files, shared pins or historical evidence were changed. These are BSP-only QEMU witnesses, not production init, hardware, SMP or recovery acceptance.

## Inputs and reproduction

[source-snapshot.tar.gz](source-snapshot.tar.gz) contains the 1,800 original input files named in [snapshot.json](snapshot.json), including all three owner checkouts, pinned boot dependencies and the pinned musl source archive. Generated SDKs/build directories are excluded from this input archive. All named input hashes were verified unchanged after the suites. Root first-party licenses and applicable vendored terms are preserved; the SDK binaries contain musl, whose notice is also retained as COPYRIGHT-musl.txt. This is development evidence, not a completed release/third-party audit.

Extract the archive into a new private directory, place the retained run-sdk.py and run-native.py beside the three extracted owner directories, then use the recorded tool versions/absolute tool-lock inputs. Run the three sys-init docs/check-*.py pin verifiers and import Aether/scripts/deps.py to call verify() (executing deps.py directly performs setup/fetch and is not the offline check). Run `python3 run-sdk.py`, then `python3 run-native.py`. Each helper derives its root from its own location. Exact original commands and preflight output are retained. Rebuilding developer entropy need not reproduce identical envelope bytes; artifact identity is recorded per run.

The SDK build verifies pinned clang/lld tools and the musl archive; both variants were rebuilt from frozen sources, not reused from older /tmp SDKs. Before target tests, source/probe/profile and envelope receipts were checked. The I/O runner also validates adapter and bad-reference-count artifact correspondence. Both kernel test copies match the same frozen baseline. `-Dsmp=false` is explicit; native-memory remains false by the pinned build.zig default (no enabling flag). This does not test native-memory functionality.

SDK commands have a 180-second outer process-group watchdog. Each complete native suite has a 600-second outer process-group watchdog; its existing commands have 120-second limits, and QEMU has a separate 30-second watchdog. All commands completed without a timeout. Source/archive hashes, rebuilt SDK ELFs/envelopes/maps, supervisor binaries, build recipes, target command logs and serial logs are retained. ISO bytes were checked against each result digest in the work directory; large ISO files are not duplicated here.

## Outcomes

| Profile | Positive | Exact rejection controls |
| --- | --- | --- |
| Supervision | Ready/output, real worker fault, peer progress, reclaim, replacement, stale-handle denial, peer stop/reclaim | Wrong detail; supervisor entry fault; withheld output; skipped backing zeroing |
| I/O | Two fresh generations: input/backpressure/seal, separate stdout/stderr, EOF, terminal exit, reclaim and stale-handle denial | Bad descriptor reference count; withheld output; skipped backing zeroing |

Each positive exits 0 with its exact pass marker. Every negative exits 1 with its expected panic and no pass marker; build failure/emulator timeout cannot satisfy a negative. [Supervision results](supervision/results.json) and [I/O results](io/results.json) preserve nine individual cases. SHA256SUMS.json fingerprints this retained evidence set.

BG-055 is complete for this checkpoint. BG-032/BG-040 next specify explicit-stop/fault I/O closure witnesses using existing operations. Service clocks, owner recovery, general services, SMP supervision, package activation and parent-death containment remain outside this result.
