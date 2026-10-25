# Sys-init native-init consumer

## Current experimental build profile

`tests/native-init.py` uses `retained-sampling-v1` by default: Rust 1.98.0,
edition 2024, x86_64-unknown-none, opt-level=s, panic=abort, static relocation,
unchanged init.ld and the 4096-byte maximum. Native source paths are remapped to
`sys-init/prototypes/native-supervisor`. No optimization-selection flag is exposed;
other builders retain their own settings. The JSON report's additive build_profile
field identifies this profile and commands retain exact compiler options. Existing
CLI arguments, schema/fields, exits and native smoke markers remain intact.

[Decision 0081](decisions/0081-native-retained-sampling-profile.md) qualifies all
127 native cases on the pinned producer. Reproduce with the command in its
[retained invocation](evidence/native-retained-sampling-2026-09-06/witness/invocation.json),
selecting a new private --work directory and the matching explicit worker receipt.
Historical opt-level=2 results below describe their original source/profile only.
This is a bounded native fixture, not a production optimization/performance claim.

## Original checkpoint

2026-09-05. [Decision 0017](decisions/0017-native-init-consumer.md) accepts Aether's
AENIN001 / ABI 6 for a bounded, independently authored sys-init policy fixture.
[Seven target cases](evidence/native-init-consumer-2026-09-05/README.md) pass on the
frozen producer snapshot. This is consumption of the new seam, not a renamed
Aether conformance client or a port of the host runtime/model.

| Gate | Consumer evidence | Accepted limit |
| --- | --- | --- |
| SI-01 clock/wait | Observe a revision change, release/stale-token rejection, immediate expired deadline, actual future tick timeout, retained completion after cancellation, pending cancellation/occupied slot, target-reclaimed completion | One registered lifecycle wait, polling/yield and delivered interrupt counts; no elapsed milliseconds, blocking sleep or suspend accounting |
| SI-02 readiness/channel mapping | Transferred writer loses old-holder authority; buffered byte from terminal owner is rejected; independently live helper remains under explicit stop ownership; fresh channel/instance rejects old references and starts empty/unready | Supervisor-launched first-party/helper transfer; no arbitrary delegation, dup or revocation tree; liveness checks are observation cuts |
| SI-03 supervisor death | Exit and UD2 each begin with one live worker, one terminal worker, two buffered bytes and one retained wait; exact verified shutdown marker follows | Opt-in whole-domain fail-closed shutdown; no supervisor restart, recovery inventory, surviving service or SMP recovery |

The main policy completes three explicit worker reclaims and reaches
`AETHER NATIVE INIT PASS`. Incorrect deadline and late-admission policies reject
at assertions 821/822. Ignoring kernel deadlines rejects at 821. Skipped cleanup
zeroing must reach the cleanup-specific panic, never the CLOSED marker. These
controls require exact context; a timeout, build failure or unrelated panic fails.

The client is 3,536 bytes within the immutable 4 KiB code bound and uses the
profile's separate stack. Static GOT entries share the immutable code page;
writable data/BSS are forbidden. Older sys-init sources/linker maps/build profiles
were not changed. Size is not a production memory/performance measurement.

## Reproduction

```sh
python3 tests/native-init.py --producer AETHER_NATIVE_INIT_EVIDENCE --summary-pin SUMMARY_SHA256 --deps PINNED_AETHER_DEPS --work NEW_PRIVATE_DIRECTORY
```

Use the producer evidence directory containing summary.json, producer-sources.tar.gz
and init artifacts. The consumed summary hash is
`86d52e49898fcb859fcb7ffd7af46310152381590753f72e6ba690f17a14c9e4`.
The runner verifies the summary/archive/report/envelope and both retained ELF
correspondences, extracts a safe private snapshot and verifies per-file producer
hashes before builds. Boot dependencies are supplied explicitly and verified by
the frozen producer checker; no automatic sibling discovery/download occurs.
It captures local policy/harness inputs, checks their stability after execution,
and records commands, logs and artifact hashes. Builds have 180-second process-
group watchdogs; the frozen QEMU runner has its separate 30-second watchdog.

The producer's existing source-rebuilt strict-musl worker ELFs are consumed as
artifacts; they are not rebuilt or authored here. Their provenance remains the
producer receipt and source archive. Local hashes establish trusted byte identity,
not publisher authenticity or complete host-library provenance. Development
bootstrap entropy retains its producer scope. Help/version return 0, invalid
usage 64, operational failures nonzero. Failed/private run evidence is preserved.

The original consumer checkpoint passed 48 host, 34 model/three mutation controls,
25 harness tests and all standards. The [offline audit](NATIVE-COVERAGE.md) now
includes these seven cases with the older 22; this audit does not rerun QEMU.
Previous Linux host validation remains a separate witness.

## Follow-through

The blanket wait for SI-01–03 producer inputs is lifted for this accepted scope.
The ABI-6 report is now in the offline catalog.
[Decision 0018](decisions/0018-native-adapter-boundary.md) specifies the next
bounded adapter extraction and service/dependent workload.
[Adapter extraction](NATIVE-ADAPTER.md) now passes nine native cases; sequential
cross-slot reuse initially exposed a kernel gate. The
[SI-04 consuming refresh](evidence/native-slot-reuse-consumer-2026-09-05/README.md) now resolves
that gate with both orders and all nine adapter cases passing.
The host model's millisecond policy is not directly portable to interrupt counts.
Broader runtime questions stay in BG-032/BG-033/BG-040; native consumer acceptance
here does not complete production init, calibrated clocks or supervisor recovery.
