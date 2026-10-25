# Interrupted import recovery

Implemented 2026-09-05 for the private-root binary experiment. Recovery is explicit adoption of an existing stage that exactly matches a caller-pinned bundle. It never repairs, replaces, or removes that stage.

```sh
sh mk/binary.sh recover "$root" "$bundle" "$descriptor_sha256" "$expected_target"
```

The arguments have the same meaning as [binary import](BINARY-PACKAGE.md). Keep the bundle and its independently selected pin available. Recovery revalidates bundle integrity, host identity, dependency record fingerprints, evidence and ownership. It then checks the existing stage's complete regular-file manifest and exact ordinary permissions recorded in v2 against that bundle. A matching missing record is published with one rename. Repeating recovery for the same committed package succeeds without rewriting its record.

No journal or remembered source path is trusted. This command cannot prove an earlier import created the stage: the caller explicitly authorizes adopting matching content. All files and parents must remain under caller control; the single-writer constraint remains in force.

## Observable states

| Interruption point or condition | Result and next action |
| --- | --- |
| Before payload publication | No final stage; use ordinary import. Recovery refuses an absent stage. |
| After payload rename, before record rename | Ordinary import refuses the occupied stage. Explicit recovery validates it and publishes only its record. |
| After record rename, before success output | Recovery validates again and succeeds idempotently. |
| Changed bytes, missing/extra file, unsupported link/type, or changed permission bits | Reject; preserve the stage and existing records. No implicit repair. |
| Changed dependency record, wrong pin/target, ownership conflict, or inconsistent authority | Reject; resolve the discrepancy outside recovery. |
| Interrupted recovery before its record rename | Existing stage is untouched; retry with the same bundle and pin. |

Recovery uses `state.sh check-register ROOT MANIFEST BUILD-RECORD DEPENDENCIES` to reuse full registration validation without publishing a record or creating a temporary file inside authority. Binary recovery's validated record lives in private scratch until its single rename. The check command can also be used directly for registration preflight; it grants no reservation and provides no concurrency guarantee.

A killed process can leave `.binary-work.*` scratch directories, and state validation can leave temporary workspace outside the root. They are not package authority and recovery does not consume or delete them. Ordinary handled failures clean their own temporary work. Power-loss durability, fsync ordering, concurrent writers, hostile path races and filesystem corruption remain unproven. SIGKILL tests establish process-interruption behavior only.

## Configuration and permission boundaries

All current files, including any file beneath `etc/`, have ordinary immutable package-content semantics. There is no configuration classification, merge, overwrite, `.new` convention or post-install hook. A locally changed configuration file is a mismatch; recovery preserves it and refuses to commit. This is the conservative baseline for a future configuration contract, not implementation of upgrades.

The bundle mode table is the authority for recovery's exact file-permission check. For v2 records, `state.sh verify` also checks file permissions. Legacy v1 records produce `mode-untracked`. Directory permissions, owner/group, ACLs and xattrs are not modeled. Set-ID/sticky bits remain unsupported.

## Validation

`tests/binary-package.sh` kills the importer after stage publication and kills recovery after record publication. It checks retry/idempotence, changed bytes, extra files, symlinks, absent stages, and permission drift, while preserving existing package records. `tests/package-state.sh` verifies that registration preflight does not publish a record. The full suite remains local and compiler-free.

Historical v1 evidence: a real zpipe check also passed in `/tmp/pkg-recovery-real.75YBky`: zlib was imported normally, then an already normalized imported zpipe stage was copied without its record to model the publication gap. Two recovery calls produced the exact original record, state verification passed, and the executable passed empty/text/binary and malformed-stream tests. A preliminary copy from the source-build stage was correctly rejected because its host receipt retained 0600 rather than the bundle's normalized 0644; recovery did not change it.
