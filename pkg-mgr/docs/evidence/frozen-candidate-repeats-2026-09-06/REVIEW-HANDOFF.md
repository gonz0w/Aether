# Independent review handoff

Status: prepared request, not an assigned or completed review. No reviewer has been
named and no message has been sent. Review the frozen experimental host candidate:

- Archive: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-release.7tdurxhw/pkg-mgr-0.1.0-candidate.tar`
- SHA-256: `9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043`
- Scope: 187 selected files, private-root host preview, current qualified macOS arm64
  profile. No native installation, deletion/pruning, service activation, remote
  authenticity, concurrency or power-loss durability promise.

Keep technical/content, clean-builder and reader reviews separate. One review
cannot stand in for the other scopes, and implementation work is not independent
approval. A changed archive needs affected review and qualification again.

## Technical and content review

Read the candidate README, CONTRIBUTING.md, docs/ARCHITECTURE.md, docs/DEVELOPMENT.md,
docs/BINARY-PACKAGE.md, docs/PACKAGE-STATE.md, docs/IMPORT-RECOVERY.md and
docs/REPLACEMENT-POLICY.md. Inspect mk/binary.sh, mk/state.sh, mk/replacement.sh,
mk/check-root.sh and the associated fixture tests. Check publication ownership,
failed-tool status propagation, handling of uncertain completed renames, preserved
pending evidence, and the distinction between hashes and authentication.

Review LICENSE and docs/RELEASE-CONTENTS.md against the actual archive inventory.
Check that omitted development references are clearly marked and that no historical
observation is presented as acceptance of this artifact. Record concrete defects,
reproduction commands and affected files. Do not mark known unsupported scope as
implemented simply because tests pass.

## Reader walkthrough

Use only the extracted package documentation for the hello-local tutorial and
bytecount workflow after documented prerequisites are available. Verify help and
manual lookup, expected stdout/stderr and exits, package/world inspection, binary
export/import, and the documented response to an interrupted or blocked operation.
Do not improvise deletion, repair or live-prefix writes. Record where instructions
are missing, ambiguous or require outside knowledge. Automated manual checks do
not replace this walkthrough.

## Captured builder witness

Follow docs/HOST-SETUP.md to capture a fresh builder and exact acquisition/setup
inputs. The original Apple installation media were not retained; an installed-tool
receipt alone cannot satisfy this review. Record a new profile if OS/compiler/SDK
changes, and retain setup failures and exact supplier/tool/artifact identities.
After setup, unpack the hash-verified archive into a private workspace and run:

```sh
python3 tests/check-host-setup.py
sh tests/check.sh
python3 tests/check-manuals.py --render-required --binary-example
```

Preserve raw logs, exit status and emitted retained-root paths. Do not count
unavailable prerequisites or unexecuted steps as passed. Network denial is a
separate boundary; this request does not claim it was enforced.

## Review receipt

Supply reviewer identity, review date, archive digest, scope actually reviewed,
commands/results where applicable, findings and unresolved questions, and a scoped
accept/reject/needs-work conclusion. Only an actual reviewer supplies that receipt.
Maintainer publication approval and the monitored security-reporting contact/triage
owner remain separate requirements. This handoff grants no publication authority.
