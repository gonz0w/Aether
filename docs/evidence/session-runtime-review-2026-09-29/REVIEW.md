# Aether-side technical disposition

Reviewer: Codex working in the Aether repository,2026-09-29. This is an automated
technical review of userland's delivered extraction and the native contract fit.
It supplies no independent human reader identity, approval or release decision.
Inputs are bound by review.json and the two external seals, with exact reviewed
runtime/application/header/builder sources copied under candidate/.

## Findings within the bounded profile

The runtime diff moves main/arguments/environment/helper-path policy into the
application, changes include paths to retained vendor bytes, routes helper policy
through an application callback, and adds a per-process start guard. Existing
bootstrap identity, FD/pipe state, public/internal mask transport, copy/rebind,
exec vector bounds, poison and finalization mechanisms remain in the runtime.
No additional kernel dispatch or authority path appears in this extraction.

Start rejects a null caller-result pointer before consuming bootstrap. A non-null
first attempt marks the image started before receiving bootstrap; failure therefore
requires image termination, as the public header states. Repeated start rejects
before transport and leaves the caller result unchanged. Copy inherits started
state; replacement starts a fresh image. This remains a single-threaded bounded
image contract; the non-atomic guard is not a concurrent initialization guarantee.
Ordinary user-pointer faults remain user-domain faults, not native grants.

Application callback admission narrows fixed helper policy. Owner-issued identity,
image admission and grants still enforce actual authority; bypassing that callback
cannot create grants. Failed-exec fixture variants deliberately exercise owner
lookup/denial. UID/PWD/paths and role results remain metadata. UART stays owner-only;
007 compatibility rebuilds do not advertise a007 supported component bundle.

The removed SERIAL_STALE_REFERENCE diagnostic is restored inside a generated
*test-only* runtime by regressions.py before compile. Its retained case therefore
continues issuing the actual stale operation rather than merely compiling an unused
macro. The maintained runtime acquires no diagnostic API. Existing compiled borrowed
memory/fork/signal sources and exact hashes preserve their reviewed contracts;
this does not constitute an all-path musl/stack audit.

Component validation requires the exact13 names, unique absolute regular inputs,
matching digests and008 schema/profile before link. Bundle verification checks an
externally selected seal, every member, complete include namespace, tools and no
symlinks before imports/build output. Existing/inside-bundle outputs reject. These
are developer trust/admission controls over a reviewed recipe, not a confinement
sandbox or native security boundary. A malicious replacement recipe requires a new
externally selected seal; pin identity alone does not authenticate its author.

## Scope by consumer requirement

| Requirement | Aether-side disposition | Remaining acceptance |
| --- | --- | --- |
| SSDK-01 |571 candidate members verify; fresh local offline parent/helper build matches native-tested whole ELFs; seven pre-link and eight bundle rejection receipts reviewed | Consumer/owner promotion and reader disposition |
| SSDK-02 | Startup guard and separate application callback/main reviewed; null/repeated-start native receipts and owner wrong-grant controls retained | Complete bootstrap exclusion/failure walkthrough and actual reader findings |
| SSDK-03 | Existing mask/copy/TLS/rebind/exec mechanisms preserved in source diff; fresh corresponding workload receipts pass | All claimed mask/initialization scope must retain exact pins; no broader concurrency approval |
| SSDK-04 | Memory component mandatory despite musl link fallback; FD/EOF/error/cleanup receipts retained | Broader memory/unsupported-path disposition and human review |
| SSDK-05 |49 completed native receipts and49 consumer comparisons reported across47 distinct workload cases plus initial repeat/bootstrap;11 serial owner hashes match producer | No full160-case suite or broad native runner/connections rerun in this extraction; independent acceptance disposition pending |
| SSDK-06 | This exact-input automated technical review and isolated rebuild are recorded | Independent human technical/reader identity, findings and disposition absent |

No newly identified kernel enforcement defect blocks this bounded extraction.
This conclusion is scoped to source comparison, checked build identities and supplied
native receipts. It does not close SSDK-01–06 collectively, publish an SDK or prove
whole-system security. Broader TTY/jobs/signals, physical hangup, persistent storage,
package/sys-init assembly and general interrupted-service recovery remain open.
SI-07 still needs a different sustained bootstrap/transport and runner/bytecount
payload;008 session extraction is not that delivery.

## Intake corrections

The initial receipt glob counted48 executions and omitted native-serial.process.json;
explicit selection now covers49 and excludes native-image.process.json, an ISO build.
The first bundle-rejection assertion treated output_created as creation by the
builder. The existing-output test intentionally starts with that directory present;
its zero command count and rejection are correct. Corrected selection checks exactly
that pre-existing exception. Both failed intake checks are retained. No producer
receipt, candidate source, native execution or acceptance predicate changed.
