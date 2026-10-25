# UL-058 NB-01 native bootstrap controls

Plan before driver changes: explicitly opt in to the reviewed combined producer
bundle via --bootstrap-controls, retaining default old pin and suite. Run the old
nine consumer cases against the new producer plus three second-binding byte
corruptions and one early-publication mutation. Link a test-only channel wrapper
that changes an actually received 32-byte native bootstrap. Count adapter channel
calls; real musl read/write/close must return EBADF, preserve sentinel, and produce
no subsequent traffic after rejected bootstrap/re-entry/launch attempt.

Exact control result: child 95, parent fixture assertion 53, broker 970/reclaimed
0. Early-publication mutation must instead report child 97 with the same parent
and broker rejection. No CONNECTIONS PASS marker in these four rejected workloads.
No remote cleanup/recovery claim. Default five client ELF hashes must remain equal
to the prior bootstrap-fix builds. New clients require all existing ELF inspections.

Use existing Clang/LLD C17, Rust/Zig/QEMU pins, strict SDK, private build outputs,
owned process groups and 30-second guest watchdog/180-second commands, 15-minute
suite budget. Verify locked producer reports/archive and member identities before
use. No owner implementation or shared API changes. Retain sources/diffs, all
attempts, raw serial logs, hashes and process cleanup. Technical review by current
task; independent review pending. Quality/format/syntax and affected native suite
required. NB-02–04 and public CLI stay open.

Actual technical review: current task reviewed wrapper lifetime (same synchronous
bootstrap stack buffer), short-read accumulation, field offsets 16/20/24, exact
count/ref/errno/sentinel oracles and mutation-only build selection. All new clients
link real musl. Three negatives produce child95/parent53/broker970; the mutation
produces child97/parent53/broker970. No remote reclamation is inferred. Original
five ELFs are identical; old producer nine and new producer thirteen cases pass.
21 host/control tests, pinned C formatting and Python 3.10 grammar checks pass.
No failed attempt occurred. Independent technical/reader review remains pending.
