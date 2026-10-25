# Exec shared-holder preservation — 2026-09-10

The independently admitted peer retains shared file records across native source
exec and source exit. Input advances a/b/c/d through one owner position; stdout
remains usable after the source's CLOEXEC holder disappears. Exact write/readback
and three final-close receipts per generation precede cleanup. Two generations
produce source62, peer63, backend17 and six reclaims.

All192 connections cases, five launch cases and host tests (99 Python, five Rust
descriptor tests) pass. Early stdout close rejects2080; a private peer offset
rejects1903. Both controls fail before reclaim for the named reason. This is
bounded producer evidence, not public fork/execve, independent SDK/dash acceptance
or release readiness.

## Implementation and limits

Reuse the existing descriptor plan, two-row holder matrix, per-connection reference
validation, backend and final-close helper. The plan drops the source's holder,
not the peer's. Only absence of another holder permits backend release. The peer
uses the replacement ELF with the existing worker argument; no fourth image,
worker, channel or service is added. Source cleanup is deferred until all peer
observations succeed, so the negative controls cannot hide partial reclamation.
The pre-code selection and simplicity assessment are in NATIVE-SHELL-STARTUP.md.

No kernel ABI, SDK, sibling repository, dependency, release pin or production
ownership policy changed. Fixed RAM backend state and the source-first exit order
are the limits. Peer-first exit/fault and incomplete shared final-close recovery
remain separate, as do unknown commit receipts and consumer staging acceptance.

## Storage and preparation

Disk exhaustion prevented the initial verification command from starting. Only
225 MB of disposable Zig cache was cleared. A slow random-access archive check
was interrupted and replaced by a complete streaming pass. duplicate-review.json
records6,420 unpacked files matched against their sealed archives and inventories.
The maintainer replied to continue after the specific cleanup request, but23 GB
had become available by then: both unpacked directories were retained and no
qualification evidence was disposed. preparation-checks.log retains the earlier
documentation checks. Native attempt1 rejected peer startup at215 and owner1950 because the fixture
supplied0x77 references to the strict0x76 parser. The corrected fixture uses the
same local reference values on separate private connections; parser validation
and connection-selected authority remain unchanged. Full attempt artifacts,
logs and sources are retained in attempt1. Final qualification used frozen sources.

## Reproduction and integrity

Use the complete connections and launch commands in NATIVE-CONNECTIONS.md with
the recorded SDK/tools lock. timing and results files retain commands, tools,
artifacts and exact outcomes. run-sources records the execution input snapshot;
sources additionally captures final documentation. Archives are read back against
recorded hashes. change.patch compares the preceding bootstrap-rejection packet.
compatibility.json verifies every189 older case: kernel load segments and entry
remain identical; only nonloaded .debug_line differences are permitted. Any changed
older exec owner payloads are identified explicitly; other payloads match outside
developer entropy bytes. qualification.json records counts, sizes and changed files.
final-checks.json retains host, format, workflow, standards and diff checks.
collect.py verifies the prior sealed manifest and four-file simplicity snapshot.
manifest.json seals this packet. Reader review and consumer acceptance remain pending.
