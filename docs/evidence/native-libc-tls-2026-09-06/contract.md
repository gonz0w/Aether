 — 2026-09-06

Before implementation: exercise the existing child storage ABI with actual musl
1.2.6 __copy_tls and child libc calls, rather than invent another kernel operation.
The conformance adapter owns an explicitly bounded initialization of the private
pthread structure using matching upstream headers. It copies the real TLS image,
sets self/locale/canary/sysinfo and the known bounded child ID, but does not publish
a libc thread-list entry or claim pthread_create/join, cancellation, locks or TSD.
Only pthread_self, errno access and bounded snprintf are selected child operations.
The child still exits through the native grant; libc exit policy remains outside
this witness. No kernel, sibling, dependency pin or shared standard changes.

Use the supplied strict libc archive and exact musl source tree matching its
receipt; hash/archive consumed private headers and source identity. Reject missing
or mismatched inputs. Allocate the existing three-page TLS range; initialize within
its middle page only if libc.tls_size fits 4096 bytes. Failure must reject rather
than truncate. The real TLS template must initialize a child-local cookie; child
mutations and errno must not alter the parent's values across scheduling and join.
The initialized canary supports stack-protected C/libc functions. No user pointer
or private libc structure becomes a new kernel contract.

Add an optional --libc-tls selection to the existing thread harness. Reuse storage
admission, alias, stop/replacement, guard-fault and exact pin-bypass controls in
both memory profiles. Require actual child libc/TLS checks before successful
termination. Re-run older storage/stack/wait/thread suites and host checks on frozen
sources. Kernel/memory/image/M4 bytes do not change; their preceding qualification
remains scoped evidence, not a fresh run. Preserve all attempts and pinned C format.
This is an integration witness, not companion acceptance or general libc threading.

The libc TLS suite also deliberately substitutes the parent self-pointer in the
child TLS structure; exact terminal assertion 291 must reject it. Each memory
profile runs seven cases. Private upstream headers are system includes; first-party
C retains -Wall -Wextra -Werror. The build defines musl's hidden visibility macro
exactly as src/include/features.h; no broad first-party warning suppression applies.
