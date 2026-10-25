# UL-007/081/082 per-process descriptor views review

Pre-code plan,2026-10-21. Sys-init now prepares native endpoint adaptation and
host-consumes the ten-member remote-description input. Next add central broker
per-process views for existing shell1/children2–4. This is local policy/host
composition, not native authentication, process admission or a new shell protocol.
Consume exact decision0194 startup.rs bytes for canonical ABI29 identity rather
than duplicate PID/handle/memory/parent rules. Pin full56-member source packet
and previous ten-member remote candidate first. BSD-2-Clause preserved verbatim.

One AF07 client/source,13 shared descriptions total,13 file FDs per view and
four views for existing process roles. Default single-view core remains one table
through const specialization; no old ABI/wire/default/native quota change. Share
existing read/seek/dup/close/cloexec algorithm; last-close checks ALL views. Fork
copies bindings/flags after trusted native admission, retaining common handles/
offsets with no lookup/new native grant. FD flags change independently afterward.
Parent must be active shell1; child slot2–4 and next generation1..15. Shell1 starts
at1, advances sequentially<=3 only after all prior views settle. Generation history
never resets. No nested-child fork or new roles/lifetimes silently supported.

Opaque process key is scoped to service epoch and exact canonical identity. Only
trusted dispatcher calls admitted-shell/inherit/current/settled from authenticated
native observations; canonical labels do not prove admission or confer authority.
Copy is atomic local state, after prevalidation; caller freezes parent during
actual native copy/setup. Native rejection must not call inherit. Failed exec
must not call destructive cloexec commit. Process settled is permitted only after
native/endpoint settlement is confirmed; unknown cleanup aborts admission and
preserves ledger state, not a fake successful unregister/reclaim. Any final-close
failure retires whole shared source/table; no replay. Parent release retains live
child aliases. New process generation cannot consume stale key/observation.

Rust2021/no_std, no allocation/unsafe/dependency machinery; pin Rust1.98/native
libraries, helper and immutable77-member AF07 before test/build. Generic native
libraries only; no concrete linked code/stack/heap fit. Local default12, client12,
remote8 regressions plus process inheritance/current/stale/sequence/exhaustion/
shared offset/per-view flags/final close/failed-open/fatal cleanup tests against
actual sealed AF07 service with synthetic storage. Compiling semantic omissions
must fail assertions. Actual minimum/current Python; per compile60s/test30s,
16MiB streams, clean env/build-only roots. Retain failed attempts/source/checker
versions, compact/read back before removing generated roots. Quality, syntax,
format/Clippy and inventory/whitespace required; independent reviews remain open.

Foundations O/I/E, Distribution PX, CR/TD/SE and local stricter limits apply.
Simpler alternative: copy data into independent per-process descriptions or add
four clients. Neither preserves shared open-file offsets/final-close semantics;
four clients would duplicate protocol ownership/authority. Const-specialized
views reuse one algorithm/source, removing that otherwise necessary duplication.
Borrow proven shared-open-description/per-FD-flag idea, defer full VFS/POSIX/fork/
loader transport. No immutable executable trust or general process service is
invented. Exact process/path/binding/exec messages and matching dispatcher/native
qualification still remain UL-007/081/082/M3/R1 work after this host milestone.

Final implementation-agent source assessment: exact full stored keys contain
service epoch and all canonical instance fields. Removing duplicate explicit
epoch comparison leaves the full tuple comparison as the sole membership check;
foreign-epoch and stale-instance controls now exercise that real boundary.
Validation precedes local publication/source effects. Child view copy shares
handles/offsets and copies flags, while indexed changes remain per process.
Final close scans all views, not only caller. Generation history persists after
settlement; shell replacement waits for every occupied view. Busy disconnect
keeps the live source. Failed source/close retirement closes admission, clears
file references and preserves unresolved process ledger occupancy. No canonical
label, local state transition or read-only content claims native authority or
successful copy/exec/reclaim. Native freeze/admission/settlement are documented
caller obligations, not host-test claims. Test-only fixture duplication keeps
single-/multi-view suites independently reproducible without a test framework.

18 process-profile tests/eight omissions, local12/eight and default remote8/eleven
pass on actual3.10.21/3.14.7. Per-suite native generic-library bytes match. Default
Clippy/rustfmt/warnings/unsafe denial, quality/standards/Experience/inventory,
minimum/current syntax and whitespace pass. Unchanged client qualification is
reused only after source equality checks. No independent owner/reader review,
native linking/resource fit/IPC/copy/exec or broad sanitizer/security/conformance
is asserted. Follow-ons remain in UL-007/081/082/M3/R1.

All fourteen exact attempt roots, source baselines/checker versions, logs/results
and binaries are retained in attempts.tar.xz; every member hash/size read back
before removal.188533400 logical bytes removed,12196884 archive bytes retained;
physical reclamation not measured. Initial random-seek xz readback was interrupted
before any removal; the same complete archive passed one streaming verification.
retention-prior-attempt.json records that incomplete retention attempt. No runtime
tests or native guests were replayed. All original candidates/evidence remain.
Source-only15-member seal:
95e67913a455612039941eaeafa96ff6b90add7661efe0470c8a70f6d3fdda27.
