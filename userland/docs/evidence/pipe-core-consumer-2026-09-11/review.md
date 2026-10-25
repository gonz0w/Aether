# UL-007 pipe core consumer qualification

Pre-execution selection, 2026-09-11: consume the unconnected Aether pipe core
from manifest 73d0fb9aa58c422764c336807ee8a87b0e32f0732fa9c11cbc0d77813fbac51e.
Verify the retained packet entries and all 257 archived sources before use. No
sibling implementation, runtime adapter, public CLI, ABI or pin changes.

Apply Foundations O-01–05, I-01/03–06, E-01–08, Distribution PX-01–03 and local
quality TD/TC/TE and Python CP rules. Parent/child identity in these tests is
synthetic; actual authentication, readiness, terminal observation and reply
retention remain dispatcher responsibilities. Fixed 256-byte FIFO, 16-byte
requests, one child and three generations remain authoritative fixture bounds.

Select the 12 producer Rust host cases and five exact semantic mutants. Add a
consumer test through public methods only: 32 chunk schedules (write sizes 1–16,
read sizes 1 and 16) fill the FIFO, observe backpressure, free space and retry,
confirm the writer terminal, then compare every drained byte and EOF against a
separate byte queue before collection. Reject stale child writes and require
pending replies to prevent retirement. This models the substitution dependency;
it does not execute dash or establish native enforcement. Compile the unchanged
core for x86_64-unknown-none using the producer no_std wrapper. No linking claim.

Use pinned Rust 1.98.0, edition 2024, existing local compiler/wrapper; host macOS
arm64. Every command uses the existing owned process helper with private build
root, fixed environment, 120-second deadline and 16 MiB per stream. Preserve all
receipts, failures, source/tool/plan hashes and raw streams. Expected mutant exit
101 must include its named failing assertion; tool failures cannot pass. Run
rustfmt checks, Python syntax and local quality gate. No new dependency or runtime
implementation is introduced; original files are BSD-2-Clause.

Update STATE/BACKLOG/ROADMAP and the existing draft coverage entry with host-only
evidence. Existing native redirect evidence is unaffected; do not rerun it for
unchanged runtime inputs. Native pipe wiring, SIGPIPE, original substitution and
pipeline workloads remain open. Technical self-review will be recorded with the
results; independent technical/security/reader review remains pending. No M3 or
release completion decision follows from passing host checks.

Simplicity: use one small public-method transcript and the existing runner instead
of a second pipe model implementation or dispatcher simulator. A byte queue is
sufficient for byte-order/duplicate/EOF oracles. No obsolete runtime path can be
removed before native integration exists.
