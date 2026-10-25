# Configuration and replacement policy

This contract separates implemented comparison behavior from the proposed replacement transaction. Read-only preflight remains separate from mutation. The subsequent retained-payload experiment below is implemented for explicitly requested private-root replacement; existing-payload deletion remains out of scope.

## Implemented file policy

All owned regular files have the same conservative policy. A path under `etc/`, or a `.conf` suffix, does not trigger hidden overwrite/merge behavior. Recipes cannot run update hooks. Local edits, local deletion, mode drift and unowned additions remain blockers in [update preflight](UPDATE-PREFLIGHT.md).

Preflight compares three values for each path in the old/proposed record union: the old package's hash and mode, the currently observed hash and mode, and the proposed package's hash and mode. Absence is a distinct value. Size remains checked by ordinary payload verification. These comparisons produce:

| Three-way row | Meaning | Current behavior |
| --- | --- | --- |
| `package-only` | Local file still matches old package; proposed package differs | Report proposed change; other checks still govern preflight |
| `local-only` | Proposed file matches old package; local file differs | Preserve local file and block |
| `matching-change` | Local and proposed values match, but differ from old package | Preserve local file and block; do not silently adopt |
| `conflict` | Local, old and proposed values disagree | Preserve local file and block |
| `uninspectable` | Unsafe parent/leaf type, unreadable file, or unsupported permissions | Do not follow the path or infer its content; block |

Unchanged rows are omitted. A newly proposed path occupied by an unowned local file also participates in this comparison, but remains an `unowned` blocker. Local removal and package removal can yield `matching-change`; this does not authorize adopting the deletion.

This is not a merge engine. There are no `.new` files, configuration backups, syntax validators, service restarts, or special configuration metadata. Before permitting local configuration to survive an applied update, define where expected package defaults and locally maintained state each live; a single immutable record cannot honestly describe both when their bytes differ.

## Replacement design requirements

The mutation experiment operates on one package in a disposable private root and retain the complete old stage and record. No cleanup/pruning of retained packages belongs in that first experiment. A successful preflight alone is not approval to perform these steps; replacement is requested separately.

Preparation must pin old record, proposed record/bundle, target, dependency records, and world; revalidate old payload and permissions; require no local changes or reverse dependents. An identical record is a no-op. Versions are labels, so monotonic upgrade policy must not be inferred.

The current `stage/NAME` plus `state/packages/NAME.tsv` layout cannot publish a replacement with one rename. A future implementation must explicitly address these states:

| Observed stage | Observed record | Required disposition |
| --- | --- | --- |
| Old | Old | Original state, or replacement not started |
| Absent, with retained old stage | Old | Interrupted displacement; block normal readers and recover using validated retained evidence |
| New | Old | Interrupted publication; block normal readers, never report verification success |
| New | New | Committed only after both validate against the pinned proposal |
| Old | New, missing retained material, or unknown bytes | Inconsistent; fail closed and preserve evidence |

A persistent intent record and retained old payload may be necessary to distinguish these cases, with the implemented pending-reader guard described below; concurrent writers remain unsupported. Do not retrofit an implicit journal into preflight. Do not automatically restore or advance when evidence is ambiguous. The read paths must recognize a pending transaction before an apply command can be considered usable.

Acceptance for that future experiment must include termination before/after every publication step, idempotent recovery, exact old/new mode and content checks, stale preflight rejection, unchanged world/unrelated records, and zero removal of retained old payload. Power-loss durability requires separate fsync/filesystem evidence; process-kill tests alone do not establish it. Reverting package files must never claim to reverse arbitrary external or service effects.

## Current validation

The binary fixture exercises matching local/proposed changes, a local-only edit, a conflicting local configuration at a newly proposed path, package-only removal, and a symlink that remains uninspectable and untouched. The full preflight still checks ownership, dependency fingerprints, reverse dependents and installed drift. These comparison tests are complemented by the replacement boundary tests described below.

## Implemented retained-payload experiment

The subsequent user-authorized private-root experiment implements the bounded replacement described above in `mk/replacement.sh`. This opens replacement of one verified staged package, while keeping existing-payload deletion, live-prefix installation, service effects, pruning and rollback out of scope.

```sh
old_pin=$(sh mk/verify-metadata.sh hash-file "$root/state/packages/$name.tsv")
sh mk/replacement.sh prepare "$root" "$bundle" "$bundle_pin" "$target" "$old_pin"
# Use the intent digest printed by prepare:
sh mk/replacement.sh finish "$root" "$intent_pin"
```

Prepare requires a blocker-free preflight and the exact old-record digest. Identical records are a no-op. It builds/imports the proposed stage in disposable workspace, then publishes `ROOT/.replacement` by a same-filesystem rename. No existing stage or record is changed by preparation. The pending directory guards normal package/root commands until completion. Low-level file/metadata tools are not a confinement boundary.

The intent binds package name, target, old and new records, unchanged world, other state-file hashes and the saved bundle descriptor. `next/` contains the prepared payload. Its byte and mode expectations come from the pinned new record, not from a mutable phase counter. The caller supplies the intent SHA-256 to finish/retry; recovery does not accept a changed intent automatically.

Finish validates intent content, current world and unrelated records, both old and proposed payloads, and the saved bundle through existing state/preflight validators in temporary roots. It then performs:

1. Rename `stage/NAME` to `.replacement/previous`.
2. Rename `.replacement/next` to `stage/NAME`.
3. Publish the new record using an adjacent copy and rename, retaining both pinned record versions.
4. Rename `.replacement` to `replacements/INTENT-SHA256`.

The fourth rename removes the pending guard. The old stage, old/new records, intent and bundle remain retained. A removed file in the proposed version disappears from the active stage but remains in `previous/`; no old payload is deleted.

Retry the same finish command after interruption. It infers progress from expected file locations and verifies their contents before advancing. Ordinary failures and SIGKILL leave pending material available; there is no automatic rollback or cleanup of the transaction. A `record-publishing` temporary copy is accepted only if it matches the pinned new record. An interruption during that copy can leave mismatched evidence, which blocks recovery and is preserved for inspection.

Repeated finish is idempotent at the completed checkpoint: it verifies the retained intent and current new state again. Later world/package changes can invalidate that checkpoint and cause rejection; the retained history is not a general rollback interface. Interrupted preparation may leave `.replacement-preparing.*` directories, which are not authority and are not automatically consumed or pruned.

Validation covers forced termination after old-stage displacement, new-stage publication, record publication, and retained-history publication, plus before publication of the copied record; pending-reader rejection; stale old-record pins; changed payload/world after prepare; repeated completion; and preservation of unrelated records, world and the old removed file. This remains single-writer, caller-controlled filesystem tooling with no fsync/power-loss durability guarantee.


CLI delivery failure is separate from transaction failure. The binary fixture
now prepares and finishes real transactions while CLI output pipes are closed,
recovers the emitted digest from retained raw output, rejects a forged digest,
and verifies repeated finish after completed publication. Old payload/records,
unrelated records and world remain preserved. See the [CLI recovery evidence](evidence/cli-receipt-2026-09-05/README.md)
and [output retention contract](CLI.md). Receipts are observations; finish still
checks the caller's digest and current transaction state.


## Injected storage-operation failures

The host fixture also injects two ordinary failures after the new stage is moved
but before its record is published. A copy that writes only 17 bytes and returns
failure leaves the old record, both payloads, world and unrelated records intact.
The partial `record-publishing` evidence remains pending. Retry rejects it as
`invalid pending record copy`; it does not overwrite or silently repair the evidence.
A failed rename after a complete record copy retains a matching publication file;
retrying the same pinned finish completes and remains idempotent.

These are deterministic command-boundary injections in private test roots. They
exercise partial-write/nonzero-return and rename-failure handling, not a real full
disk, power loss, filesystem flush ordering or a general recovery guarantee. The
fixture never fills a host filesystem. No new repair or deletion authority is added.


Record comparisons during prepare and finish distinguish ordinary differences
from cmp errors. Read/tool errors stop before preparing a transaction or selecting
old/new record state; they cannot trigger an alternative publication branch. Six
preflight/prepare/finish controls cover error statuses 2 and 73 with unchanged target
file bytes/modes and no success report. Existing equal/different and retry paths
retain their behavior. This does not provide filesystem-race or concurrency safety.


Intent construction and revalidation require every record/world/state/bundle digest
command to succeed before its field is emitted. A failed hash cannot be hidden by
successful printf output. Ten injected helper failures cover the five digest fields
in prepare and finish: preparation publishes no pending transaction or receipt;
finish leaves the existing transaction unchanged. Complete target file/hash/mode
snapshots remain identical. These are command-failure controls, not storage
durability or publisher-authentication evidence.
