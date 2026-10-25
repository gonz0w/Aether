# UL-007 initial scoped-directory consumer — 2026-09-09

PASS for the initial AECAT003 profile: all319 original native command cases run
locally. [Native receipt](native-results.json) binds the exact case inventory,
build flags, tools, artifacts and results. [Outer receipt](results.json) records
exit0 and complete owned-process cleanup. All545 source/4311 reused SDK file
hashes remain unchanged. Quality checks pass. No failed or interrupted local attempt.

[Ten final serial checks](cwd-cases.json) independently match completed receipt
hashes and exact terminal/reclaim records:

| Selected cases | Native observation |
| --- | --- |
| No inherited PWD, matching /work, relative work, out-of-scope /missing | Client0/backend17, two generations, owner100/four reclaims |
| Missing reference, wrong rights/kind, stale generation, reserved data | Client110/backend17, two generations, owner100/four reclaims |
| Skipped directory publication | Client106/owner1501 and exact rejection panic; zero native reclaims |

The producer label `cwd-absent` supplies `PWD=/missing`; the unsuffixed case has
no inherited PWD. These are distinct tests. Negative publication is not recovery;
outer emulator/process cleanup is observed separately. All319 serial/QEMU logs
are retained in cases/, with the focused ten in cwd-cases/.

The unchanged guest/owner checks actual generated init resolving PWD to `/work`
without the former getcwd warning, while preserving parent/advisory IDs, ordinary
copy and native denial checks. Raw queries bypass the facade for foreign/stale
references, wrong selectors, unknown operations and reserved bytes. Buffer guards,
small/zero/exact/large caller sizes, allocation/free, missing/denied paths and
unchanged stat error outputs are exercised. The final wrong-selector case requires
EINVAL, preserving the producer's review-discovered routing correction.

## Scope and remaining coverage

This is one private immutable `/work` fixture with a query grant. getcwd obtains
its name through the owner; the selected stat adaptation supplies only st_dev,
st_ino and st_mode for generated init. Other fields are explicitly unavailable/
zero. The tests observe device identity100+generation and inode1; no stable identity
across arbitrary service lifetimes is inferred. General stat consumers, arbitrary
pointer probing, paths/chdir, persistent storage and native SDK adoption remain
unsupported. Caller pointers must be valid C objects under the captured contract.

The initial directory matrix is still incomplete:

- Corrupt/truncated replies, poison persistence, no retry/fallback and teardown.
- AECAT003 version and header/body truncation with no partial publication.
- Directory-reference aliasing with each stream binding.
- Mismatched directory identities and inherited PWD fallback controls.
- Forced getcwd allocation failure/ENOMEM; allocation/free success is not that test.

The five partial [metadata rows](../../../experiments/dash-native/METADATA.md)
remain open; the larger regression count does not complete them. The separate
native-main ENV configuration decision, actual main, exec/wait and pipes remain
UL-007/M3 gates. No extra startup probe or optional utility expansion was selected.

## Provenance and reproduction

Producer shell-cwd-2026-09-08 manifest SHA256:
`33d1eab6328e7c8405fc7911683c480f820fd200c17ed498ddb101d3d027951b`.
All17 sealed files verify before consumption and retention. producer-packet/
retains the source archive, receipts and interrupted producer-attempt evidence;
packet-retention.json lists verified target archives omitted from this copy.
The producer interrupted its earlier qualification after review exposed selector
routing into a stream assertion. That history is not a local failure and is not
removed by the final pass. No local source or oracle was changed to obtain success.

[Intake](intake.json) compares nine changed files with the metadata snapshot.
Kernel/build and32 imported dash objects remain unchanged. No fresh dash/libc
source build, host kernel-suite or M4 result is claimed. Actual runtime facade,
owner and fixture sources are built with the original recipe. SDK/tool identity
is bound to sdk-reuse-receipt.json and checked before use.

Run: `python3 -B docs/evidence/dash-cwd-consumer-2026-09-09/run.py` with the recorded
dependencies on the observed Python3.14.7 host. The existing owned-process helper
uses the1800-second suite deadline,512 MiB outer stream bound, controlled PATH/
LC_ALL/private TMPDIR and original guest watchdogs. Full outputs remain under
`build/dash-cwd-consumer-x26rzysa`; retained source/receipts identify them exactly.
Minimum-version execution and complete source/reader review are not inferred.

[Review plan](review.md) records ownership, source assessment, tests and simplicity.
Next: finish the focused directory/metadata controls, then actual-main configuration
and process/pipe integration. UL-007/M3, UL-016/063/081 and independent technical/
reader sign-off remain open. No sibling edit, consumer-default or release-pin change.
