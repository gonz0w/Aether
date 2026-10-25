# 0129 — Bounded native semantic content reads

BG-056 host slice, 2026-09-07. Route every JSON, serial and init envelope/image
content read through the existing 4 MiB ordinary-file reader with the checkout
root, descriptor identity checks and cleanup. Largest possible supported init
envelope is below 4 MiB; archive/firmware artifacts remain streaming-hash-only.
Preserve host-default text decoding and universal newline conversion through
TextIOWrapper over captured bytes. Keep receipt parsing/semantic oracles unchanged.

Test text compatibility, semantic-read type/size rejection after hash verification,
and retained audit compatibility. Run focused/full checks; retain source/evidence
and pins unchanged. E-01–08 scope is host read behavior, not native acceptance.
Hashing and semantic reads still capture separately; strict receipt schemas,
same-byte semantic identity and final consistency remain follow-ons.

Validation: 44 native-harness tests and all ten gates pass in run-hdspju8m.
Native audit stdout, catalog bytes and 24 native inputs remain unchanged.
Four manual lint/render commands pass. Evidence:
../evidence/native-content-reads-2026-09-07/README.md.
