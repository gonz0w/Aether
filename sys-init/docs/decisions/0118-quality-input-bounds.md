# 0118 — Quality input bounds and reference files

BG-056 host tooling slice, 2026-09-07. Require ordinary files and reject symlink
components at or below the supplied checkout root for quality inputs/references.
Read records and snapshot payloads with a 1 MiB limit, nonblocking open, descriptor
identity checks and post-read size/mtime checks. General references are existence
checks without a content-size limit. Keep stdout schema, exits and pins unchanged.

Test FIFOs, links, oversize files, controlled replacement and growth, including
record and payload paths. Run focused tests and all repository gates. No native
behavior, shared ABI, sibling or retained snapshot edits. No new dependencies.
This is not atomic directory traversal or an I/O deadline; ancestors above the
supplied root, restored mutations and changes after final checks remain outside
scope. Independent review remains pending.

Validation: 21 quality tests and all ten repository gates pass in
out/checks/run-xuuqhhmn. An initial test run caught changed missing-reference
exceptions; the existing ValueError diagnostic was restored before retry.
Manual lint/render commands pass. Success stdout, snapshot pin and 24 native
inputs are unchanged. Evidence: ../evidence/quality-input-bounds-2026-09-07/README.md.
