# Read-only update preflight

`mk/binary.sh preflight` compares a pinned v2 binary bundle with an existing registered package. It does not replace files, publish records, edit world, or authorize a later update.

```sh
sh mk/binary.sh preflight "$root" "$bundle" "$descriptor_sha256" "$expected_target"
```

Bundle arguments follow [binary transport](BINARY-PACKAGE.md). The package must already exist. Package versions are displayed literally: no ordering, upgrade/downgrade policy or version solver is implied.

Preflight validates existing authority, the complete bundle and its target, exact dependency fingerprints and bound build observations. It substitutes the new record only in a disposable candidate root, then reuses registration validation to check the resulting ownership and dependency graph. Workspace is created outside the target root; installed payload and authority are read only.

A successful comparison emits sorted change rows: `version`, `add`, `remove`, `content-change`, `mode-change`, `dependency-add`, and `dependency-remove`. Both old and proposed record SHA-256 values identify the exact comparison. Unchanged files are omitted. Additional `three-way CLASS PATH` rows distinguish package-only, local-only, matching, conflicting and uninspectable changes under the [file policy](REPLACEMENT-POLICY.md). A `remove` row is a proposed difference, never deletion permission.

| Outcome | Exit status | Meaning |
| --- | --- | --- |
| `result no-blockers-detected` | 0 | Current bounded checks passed; no update has occurred or been authorized |
| `result blocked` | 2 | Installed payload drift or reverse dependents require review |
| Diagnostic on stderr | 1 (usage may be 64) | Invalid/missing bundle or state, target/dependency mismatch, ownership conflict, or other validation failure; no usable plan |

Payload verification covers every installed package, not just the replacement target. Its discrepancies appear as `blocker installed-drift ...`. Locally edited configuration files have ordinary file semantics: changes are reported and preserved, with no automatic merge or overwrite. Unsafe types and untracked legacy permissions also block preflight.

If the proposed record differs and the package has reverse dependents, each is reported as `blocker reverse-dependent NAME`. This deliberately conservative rule requires a coordinated rebuild/review rather than assuming ABI compatibility or validating only package names. It may block changes that would ultimately be safe. A no-op bundle does not trigger this rule.

The report is an observation, not a durable transaction or reservation. Preflight has no apply command; explicitly requested retained replacement uses the separate [prepare/finish interface](REPLACEMENT-POLICY.md). Single-writer/caller-controlled filesystem assumptions remain; a future replacement operation must revalidate all inputs. Power-loss recovery, configuration merging and existing-package deletion remain separate scope decisions.

## Evidence

The compiler-free binary fixture builds and registers version 0.2 of its app with changed content, changed executable permissions, an added file and a removed file. Tests compare installed hashes and modes before/after preflight, preserve a local edit through a blocked report, and block a proposed base-record change with a reverse dependent. A destination-only package owning the proposed new path causes ownership-conflict rejection with no plan output or mutation. Existing bundle rejection and SIGKILL recovery checks continue in the same suite.


Comparison and observation producers run separately from sorting. A producer or
sort failure stops preflight before its report header, so partial intermediate
output cannot masquerade as a complete comparison or a no-blockers result. This
ordinary tool-failure boundary is covered by twelve empty/partial-output fault
cases; package files and records remain unchanged. It does not establish hostile
filesystem-race resistance, concurrency safety or full-storage durability.

Record equality uses cmp status 0 for equal and 1 for different. A comparison
error aborts before emitting the preflight report; it cannot be treated as an
ordinary record change even when there are no reverse dependents.


The old/new record digests in the final report must both be calculated successfully
before emitting even its header. Four injected failures cover each hash with empty
output and valid digest output accompanied by a failed exit status. Every case
rejects without report bytes or target file/hash/mode changes. A plausible digest
alone cannot substitute for a successful hash command. Successful report fields
and ordering remain unchanged.
