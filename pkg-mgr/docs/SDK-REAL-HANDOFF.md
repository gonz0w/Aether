# Real SDK package handoff to userland

2026-09-07. Owner-side registration/export/import/recovery now passes for the
235-file retained SDK under userland's accepted target. This is private inert data
transport, not compiler, source-trust, native execution or release qualification.

Use [the result receipt](evidence/sdk-real-transport-2026-09-07/attempt-1/result.json)
for exact source/imported/recovery roots and bundle location. The returned bundle is:

```text
/Users/cam/DEV/pkg-mgr/work/sdk-real-ws7xos_4/source/binaries/aether-musl-sdk
```

Descriptor SHA-256:
`f26817a7371bf61a6dca40c8d51ad4267e4f25a75bcf77a1776629a60cb9a6dc`

Target SHA-256:
`1b9c2fedc9cebba0785c4f4ec5157abaf580e886eae3cb8f809375a70062ab8e`

The ready imported SDK is beneath:

```text
/Users/cam/DEV/pkg-mgr/work/sdk-real-ws7xos_4/imported/stage/aether-musl-sdk/usr/local/lib/aether-sdk/musl-native-experimental/usr
```

Treat these paths as retained local artifacts, not permanent installation prefixes.
Reverify descriptor, full target pin, record, blobs, file modes and both selected
receipt hashes against the returned evidence before consumption. Ordinary binary
import is inappropriate; use the [explicit SDK branches](SDK-TRANSPORT.md) for
another private-root transfer. Nothing was sent remotely or installed into a sibling.

[Evidence](evidence/sdk-real-transport-2026-09-07/README.md) includes the exact capture
script, source/tool hashes, all command outputs, records and manifests. It records
six real denials and the killed-stage/recovery/idempotence sequence. Packaging
observations do not fill in original unrecorded host provenance. The data package
has no package dependencies; selected compiler and native adapters remain explicit
external prerequisites, and their consumer bindings still need evidence.

Next userland work: independently verify the returned artifact identities, then
SDK-05 compile/link using the imported SDK and recorded compiler/linker/adapter
inputs, without ambient header/libc/helper fallback. Missing required inputs must
fail. SDK-07 needs stale static consumer/rebuild evidence and SDK-08 requires the
matching separately qualified native producer. Return consumer results separately;
none is inferred from successful package transport or prior native witnesses.

## Subsequent static-consumer package witness

The [record-level SDK-07 experiment](SDK-STATIC-BINDING.md) now connects userland's
retained relink to direct package dependencies and exact manifest-bound input
records. It detects the changed SDK revision despite identical ELF bytes and
preserves the baseline root. This is an explicit one-off plan, not automated SDK
replacement/rebuild enforcement; no additional native acceptance is claimed.


The [real-input planner handoff](SDK-REAL-PLAN.md) now exercises explicit KV
bindings through the read-only helper, including missing/stale rejection and a
synthetic transitive dependent around the real ELF. It also records userland's
new matched bounded native result; earlier NOT RUN observations remain historical.
No changed-SDK admission or independent release approval follows.
