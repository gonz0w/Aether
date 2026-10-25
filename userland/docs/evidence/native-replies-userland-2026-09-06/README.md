# Native reply uncertainty — UL-058 NB-02

Three independent native probes consume actual complete service replies before
simulating lost read, malformed read metadata or lost close acknowledgement.
Real musl read/write/close must report exact errno. Failed read preserves the
caller buffer; lost close remains consumed locally. After one injection, all
further file, launch and collection calls must make no adapter channel calls.
The lost-close witness first reads abcdef and writes 6-newline before injecting
at the third reply. The standard adapter source is unchanged.

Successful local safety checks end in child84, then the finite parent asserts53
and the broker rejects at970/reclaimed0. The private disabled-poison adapter is
caught on its first forbidden channel attempt at child94 before that trap reaches
the service; parent53/broker970 still required. All four must lack the normal
success marker. This is native uncertainty handling, not remote recovery or
successful reclaim after failure. The wrapper counts the adapter transport only.

All 17 combined new-producer cases pass, including nine ordinary and four prior
bootstrap controls. Nine default old-pin regressions and 21 host cases also pass.
Nine previously qualified client ELFs are byte-identical; four new reply ELFs pass
all existing inspections and link real musl calls. All suites pass first attempt;
no hidden failed run. Owned host process cleanup is recorded separately from the
intentional native rejected workloads. C formatting and Python grammar pass.

Sources, private mutant, maps, artifacts, exact terminal logs, pins and command
receipts are retained here. Large images/checkouts stay under the build paths
in summary.json. The already reviewed producer archive remains in the prior
runner-owner-review evidence. No shared API, default pin or owner source change.
NB-03/04, public parser/carrier integration, ASan and independent reviews remain.
