# Aether release scope and acceptance

Maintainer decision, 2026-09-06: Aether is the only release target. macOS/Linux/BSD
are not package-manager release targets. Host tools remain useful development and
cross-build infrastructure; their passing tests are not native acceptance. Cam
will perform the reviews. Assignment does not imply those reviews are complete.

This supersedes the [earlier host-preview release plan](HOST-RELEASE.md). Do not
require reconstruction of the old macOS/Xcode installation or an independent
macOS builder to release for Aether. Aether build inputs and the actual native
consumer still require exact identities and appropriate executable evidence.
Shared requirements remain in Aether-standards; this is pkg-mgr's local release
scope, not a new cross-project standard.

## What is established

The shell/make package-manager prototype and private-root operations pass their
host fixtures, manual examples, publication audit and repeated recovery runs.
Archive 9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043
is a frozen host-tested source baseline for review, not an Aether release binary
or an installable native package manager. Preserve its bytes and existing evidence.
Previous host qualification remains valid within its original scope.

The project also has separately bounded package-consuming native transports.
Neither those transports nor the host test suite proves that bin/pkg-mgr, POSIX
sh/make and its Unix helpers execute on Aether or that package mutations persist
across reboot. Do not substitute a target label for an executable witness.

## Active acceptance work

| Gate | Concrete evidence required | Current boundary |
| --- | --- | --- |
| Review | Cam's actual technical/content and workflow review, identifying reviewed source/artifact and findings | Assigned to Cam; pending |
| Native execution | Select a documented Aether execution path and prove its prerequisites and package operations on the target | No native shell/make package-manager witness established |
| Native storage/publication | Owning contracts for package paths, file types/modes, publication, interruption and persistence; package-consuming tests on the agreed storage profile | Host/private-root evidence only for package mutation; no new live-prefix or deletion authority |
| Aether build/artifact inputs | Exact kernel/userland/toolchain/package identities, build commands and consuming-image evidence for the selected profile | Must be attached to the actual Aether release; old Apple installer retention is not a gate |
| Package/service boundary | Preserve inert metadata and separate activation authority; include service integration only with an accepted sys-init contract | Installation does not start services; keep optional integration outside scope until accepted |
| Release assembly and reporting | Aether-specific artifact inventory/notices, supported scope, monitored security contact/triage owner, actual review results and maintainer publication decision | No native release assembled or published; contact still unspecified |

Do not add a compiled core, daemon or substitute package implementation merely to
bypass missing userland primitives. First pin a concrete consumer contract and
show the smallest executable path. Current private-root restrictions and shared
standard pins remain unchanged. Native work may resume within existing authorized
integration scope; production/live-prefix installation needs its own explicit scope.

## Companion status checked for this decision

Read-only review of current sibling tracking on 2026-09-06:

- Aether's STATE records the combined runner startup/argument/result mechanism as
  ready and directs consumers to a concrete handoff rather than a new blanket
  kernel API. This is not a native package-manager witness.
- Aether-userland's final next-action section keeps UL-058 remaining native boundary controls and
  UL-059 public aether-run startup/result work active. Twenty-two bootstrap host
  scenarios and nine legacy native regressions are now verified as owner evidence;
  they are not the public consumer. Its later CB-08–13 host transfer/reply evidence
  also verifies (53 scenarios and two mutations). NB-01 now has four verified native
  rejection controls. NB-02 now has four verified native reply-uncertainty controls;
  NB-03/04 remain open. Its producer integration
  review says public parser/combined consumer adoption is still pending, and it
  explicitly makes no POSIX shell claim. Provider evaluation is separate work.
- sys-init's current stage identifies BG-058 confirmed-result mapping as active;
  earlier accepted lifecycle primitives should not be reopened as blanket blockers.

The [package handoff review](NATIVE-COMMAND-CONSUMPTION.md) now verifies the current
UL-058 bootstrap and producer inputs. Next integration step: consume the completed,
separately pinned UL-059 public consumer when delivered; do not relabel its legacy
runner as that consumer. Keep runner
acceptance separate from native shell/build and package-storage readiness. Read
current owner evidence when implementing; these observations are not immutable
release pins and do not authorize editing sibling implementations.

## R1 boot-to-shell workload reconciliation — 2026-09-06

Aether's [R1 roadmap](../../Aether/.planning/ROADMAP.md) now requires an interactive
serial shell, persistent files, filesystem-backed execution and native package
management in one assembled system. Its R1-05 requests install/list/verify/run,
reboot persistence and removal. This is a companion requirement, not evidence
that pkg-mgr implements it or authority to delete an existing payload. The local
no-deletion/live-prefix restriction remains until a concrete removal contract is
explicitly opened. A release satisfying R1 cannot silently omit this gap.

The smallest proposed package workload is the existing bytecount 0.1 source and
license in recipes/bytecount. This is a test choice, not base-package selection.
First use a locally supplied, correctly target-built v2 bundle in a disposable
Aether disk/root. Retain the shell/make implementation. Do not rename a host target
or reuse the host executable as a native payload: its current host.kv production,
compiler target, runtime fingerprint and package admission need an agreed native
identity and matching build evidence before import can pass legitimately.

After native prerequisites are established, the existing command sequence is:

```sh
# Run from the package-manager source tree on Aether.
# root, bundle, bundle_sha256 and target are explicit, previously verified inputs.
make -s -f mk/pkg.mk ROOT="$root" init-root
sh mk/state.sh init "$root"
bin/pkg-mgr --root "$root" --format tsv import "$bundle" "$bundle_sha256" "$target"
bin/pkg-mgr --root "$root" --format tsv list
bin/pkg-mgr --root "$root" --format tsv files bytecount
bin/pkg-mgr --root "$root" --plain verify
printf abcdef > "$root/input"
LC_ALL=C "$root/stage/bytecount/usr/local/bin/bytecount" --decimal < "$root/input" > "$root/output"
```

This is a proposed target workload using existing syntax, not a runnable native
recipe today. Package paths do not grant execution permission: the shell/runner
must obtain independently authorized filesystem-backed execution and I/O grants.
The authoritative output oracle is exactly two bytes, `6` followed by newline,
read back independently. Save the imported record, manifest, modes, original BSD
license and a separate unrelated sentinel. Reboot the same disk/image; rerun
list/files/verify and bytecount, compare the recorded bytes/modes and sentinel.
Do not initialize a new root after reboot and count it as persistence.

| Prerequisite/owner | Evidence needed for this workload |
| --- | --- |
| Userland shell/tools | Real shell scripts, external commands, redirection, environment, pipes, exit propagation and traps used by the existing helpers; GNU Make baseline or an explicitly tested adaptation; required awk/sed/sort/find/cmp/hash/stat/copy/move and other invoked tools from the exact selected source |
| Aether/userland execution | UL-059 public consumer plus filesystem-backed program loading and scoped stdin/stdout/stderr; fixed boot-image grants alone are insufficient |
| Storage service | Path traversal, regular files/directories, mode queries/changes, exclusive temporary creation, rename/copy and explicit flush/persistence semantics; errors must reach the shell |
| pkg-mgr | Native target/fingerprint admission, exact record/payload/license verification and import/recovery evidence in the selected root; no helper rewrite or weaker identity check to bypass a missing primitive |
| sys-init | Start required storage, terminal and process services and deliver the shell grants; package import never starts services |

Before an executable target test, derive the complete tool/syscall inventory from
the pinned selected path and reconcile it with the actual userland providers.
This table is a workload brief, not a claim that every required tool is listed or
available. Python stays a development evidence tool, not a target runtime need.

Negative acceptance must preserve an unrelated sentinel and distinguish corrupt
bundle rejection, wrong target, denied storage/execute authority, write failure,
and interruption during publication. Inspect the retained stage/record and use
only recovery states permitted by IMPORT-RECOVERY.md. A disk flush/reboot witness
and declared interruption cases are required before a durability claim. Existing
host recovery tests do not establish those filesystem guarantees.

Next package work: reconcile the delivered native shell/tool and storage contracts
against this path, then adapt only demonstrated gaps and run it on one pinned
assembled image. NB-03/04 and UL-059 remain immediate runner dependencies, but are
not the full R1 release checklist. Removal and supported update/recovery scope need
a separate bounded package contract before R1-05 can close.

## Source-derived R1 prerequisites — 2026-09-06

Read-only inspection of the selected init/import/list/files/verify path identifies
these concrete requirements. This refines the workload above; it is not native
provider acceptance or an exhaustive syscall inventory.

| Current source seam | Required behavior or unresolved adaptation |
| --- | --- |
| mk/check-root.sh | Existing empty absolute directory, caller-owned mode 0700, usable HOME distinct from the root, physical cd/pwd, numeric ls -nd and id -u; reject symlinks/hard links and special files; noclobber creation of the fixture marker |
| bin/pkg-mgr | Writable TMPDIR (defaults to /tmp), mktemp -d, separate stdout/stderr capture, status propagation, HUP/INT/TERM/EXIT traps, cat delivery and cleanup; human verify additionally uses cli-render.awk |
| mk/state.sh and state AWK files | Environment-aware awk, tab-separated records, associative arrays, regexes and file arguments; sed extraction, C-locale sort, wc -c and tr -d whitespace; find -exec sh ... {} +, -links +1, grouped expressions and reliable failure status |
| mk/file-mode.sh | Either stat -f '%Lp' or stat -c '%a' with real ordinary permission bits; no success based merely on access checks, fabricated modes or unsupported stat options |
| mk/verify-metadata.sh hash/manifest path | One working SHA-256 provider: sha256sum, shasum -a 256, sha256, or openssl dgst -sha256; exact bytes/size, canonical digest parsing and nonzero tool failures; find, C-locale sort and private temporary output |
| mk/binary.sh import | cmp -s, cp and cp -R, mkdir -p/-m, chmod, mv, mktemp, dirname, uname -s/-m and manifest-bound metadata; candidate verification before stage/record publication |
| Existing cleanup paths | rm -rf of owned temporary output and the invocation's uncommitted new stage; do not confuse this existing bounded cleanup with an installed-package remove command |
| mk/pkg.mk init-root | GNU Make include/conditionals, foreach/call/subst quoting and exported recipe variables; no compiler needed just to initialize/import a prebuilt bundle |

Shell support must include nested command substitution/subshells, functions,
parameter expansion, quoted and unmatched glob behavior, read -r with tab IFS,
redirection and pipes, command -v, test file predicates, umask and set -C. The
scripts re-execute sh from find and helpers; a prompt that only launches one fixed
program does not satisfy this path. /dev/null is used throughout. Some verifier
AWK diagnostics use /dev/stderr, which must work or receive an explicit tested
adaptation. The source-derived list includes alternatives: it does not require
all four hash providers or both stat dialects on Aether.

Two package-specific changes need contracts before implementation:

1. **Native artifact admission.** mk/package-evidence.sh currently writes
   target_runtime=host-only and aether_compatibility=not-proven. mk/binary.sh export
   and import explicitly require host-only; target.kv uses host-binary-target-v1
   and compares uname results plus the supplied compiler target. An Aether payload
   therefore needs an explicit native observation/admission design and positive/
   negative fixtures. Preserve host v2 bundle behavior; do not remove these checks
   or manufacture host-only metadata around an Aether executable. The native ABI,
   runtime and toolchain identities must come from the selected owner handoff.
2. **Durable publication.** Current stage/record moves and shell traps do not issue
   filesystem durability barriers. A successful mv or orderly reboot cannot alone
   prove interruption safety. Establish the storage owner's flush/rename ordering
   and crash outcomes, then choose a narrow package publication adaptation with
   retained power-cut/error evidence. Do not invent a successful fsync stub.

This supplies actionable requirements while NB-03/04 and UL-059 are pending. The
next implementation should use a delivered native identity/storage contract to
change these exact seams, with wrong-runtime/ABI rejection and unrelated-data
preservation as required oracles. Existing receipt formats and runtime remain
unchanged by this inspection.

## Runner progress reconciled — 2026-09-06

The [mapped handoff review](evidence/runner-mapped-handoff-review-2026-09-06/README.md)
supersedes earlier NB-03/04 and wholly pending parser/startup notes. Their scoped
native witnesses now exist, including collected-result mapping and uncertainty
controls. A separately named package transport consumer can now be developed;
complete public CLI, native shell/tools, filesystem-backed execution and package
admission/durability are not established. Aether's new Rust block transport and
flush/fresh-VM witnesses are block-level evidence, not a filesystem service or
package publication contract. Those owners' R1 integration work remains required.

## Bounded native command consumption — 2026-09-06

The [package-staged command consumer](evidence/native-command-consumer-2026-09-06/README.md)
now reconstructs and boots all 53 pinned cases: 22 successes and 31 expected
rejections. This supersedes the transport-consumer-pending statement above.
Native execution of the shell/make package manager, filesystem-backed loading,
native artifact admission, durable publication and removal remain unproven or
unimplemented; this bounded command witness does not close those R1 gates.

## Current owner dependencies — 2026-09-06

| Owner | Next concrete handoff | Package implication |
| --- | --- | --- |
| Aether, UP-02 | Review userland's [local-outcome packet](../../Aether-userland/docs/RUNNER-OWNER-HANDOFF.md), define output roles/no-child lifecycle and return a pinned producer bundle | Required for native runner help/error consumption; the prepared proposal is not an accepted API |
| Aether and userland, R1-02/03/04 | Shell/tools, filesystem namespace and file-backed execution; native build/runtime identities and publication/flush failure semantics | Required for actual pkg-mgr import/verify/run/reboot; 8-MiB backing and block flush tests do not provide these contracts |
| pkg-mgr | Consume returned contracts, adapt native admission/publication and qualify the bytecount workload | Current 53-case transport stays accepted; no identity bypass, invented filesystem guarantee or installed-payload deletion |

Current userland tracking reports 66 native controls, beyond the package pin's 53.
This checkpoint does not adopt that newer receipt or claim its package consumption.
The next R1 step requires the owner interfaces above. The owner packet is prepared
but unsent/unaccepted; no message, sibling task or background monitor was created.
