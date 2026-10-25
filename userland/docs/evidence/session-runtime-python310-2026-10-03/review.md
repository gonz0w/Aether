# UL-007 / UL-063 bounded builder minimum-interpreter repair

Python host tools use the local CP-01–03 / Python3.10+ profile. The runtime bundle
builder and component validator call hashlib.file_digest, absent on Python3.10.
Reproduce both failures with the retained pinned3.10.21 interpreter before edits.
Replace each use with a simple1MiB incremental SHA256 loop. Hash semantics, file
validation, component admission, support-module isolation and process ownership
stay unchanged. Native C, ABI23/profile, recipe/compiler/SDK and helper unchanged.
No released pin or immutable candidate is rewritten. BSD-2 applies to original
Python; inherited source/SDK/upstream terms preserved.

Verify previous whole evidence seal and corrected bundle seal before extraction.
Retain old source, every attempt and receipts. Test empty/multichunk hashing,
valid and missing/stale/duplicate/wrong-profile component manifests, seal/member
corruption and cached fake process/components with exact build output equality.
Execute on pinned3.10.21 and current3.14.7. All compiler invocations remain owned,
60second/16MiB bounded, checked cleanup. Whole suite budget ten minutes. Identical
native ELFs reuse the49 previously qualified native executions; no new native
execution or wider Python/module/security qualification follows.

Small streaming loops are simpler than an added compatibility module/dependency;
no obsolete runtime mechanism is removed. Required quality/syntax/whitespace and
bundle archive readback before completion. Local technical review by current Codex
agent; independent technical/reader acceptance still pending. Missing package,
assembled-target, broad POSIX and SSDK-06 evidence stays incomplete.
