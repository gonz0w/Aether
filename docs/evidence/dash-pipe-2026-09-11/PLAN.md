# Actual dash command substitution

Requirement: connect the tested pipe/SIGPIPE/FD/fork/wait seams to pinned actual
dash. First execute `value=$(echo pipe); result=$?; echo "$value"; exit "$result"`
through existing AENMX002 and the independent bounded stream backend. This keeps
UART timing separate while proving real parser/builtin child/output/wait behavior.
Two actual parent/backend/copied-child lifetimes produce six reclaims. Each pipe
starts at generation1; same-parent repeated pipe generations and serial integration
remain the next extension, not claimed here. No OpenZFS or sibling work is required.

Expose public pipe() only in this opt-in producer client using the tested private
adapter. Keep five-binding fork v2 and exact canonical snapshot for FD0/1/2/3/4/10.
Use real musl fork/wait3 and pinned dash main/jobs objects; do not synthesize exec
or status72. Child redirects pipe writer to stdout with dup2 and closes aliases.
Owner dispatches ready parent/child requests, preserves stdio holders and offsets,
forwards ordinary stdio to the backend, and sends pipe requests to the existing
safe core. The parent must read exactly `pipe\n` through EOF before collecting the
real child exit0. Dash strips the newline, then its outer echo writes `pipe\n` to
stdout. Check backend readback before final close, all stdio positions and exact
child/parent/backend terminal states before six actual reclaims.

Before fork, serve bounded cwd and no-child wait queries as in existing dash
profiles. Copy starts only after the complete validated snapshot and exact freeze
token; stage holders before copy and publish child access after readiness. Wait
returns no-child/zero only for the actual state and requested WNOHANG; retain the
result until its existing acknowledgment. EOF depends on real writer holders,
not wait completion. Unsupported exec remains ENOTSUP rather than a fake success.

Forbidden: fake shell output, pipe writes forwarded to the terminal backend,
child I/O before readiness, lost/shared descriptor aliases, EOF before data,
reclaim before wait acknowledgment, ambient authority or quota increases. Controls:
wrong v1 fork header must reject at2174 before copy; false child status256 must
make actual dash exit1 and owner reject at2176 with zero reclaims. Unexpected
faults, stalls and partial publication contain this fixture; general recovery is
not claimed. Existing native pipe failure profiles remain complete regressions.

O-02–05, I-01/03–06, E-01–08 and local Coding/Testing/SE-01–05 apply. Aether owns
this producer; userland owns installed SDK and independent acceptance. No kernel
source, sibling, released pin, new service or resource limit change. Keep policy
in the private Rust owner, reuse the fixed pipe core and stream protocol rather
than create a generic VFS/process server. A separate focused dispatcher keeps
this actual-dash workload distinct from intentionally scripted pipe controls.
No old path is removed until its consumer replacement is qualified.

Existing native calls borrow bounded stack buffers; no new unsafe block, allocator
or dependency. Original sources use BSD-2-Clause; upstream objects retain pins and
terms. Pinned Rust1.98.0/edition2024 and clang-format21.1.8 remain in use; preserve
legacy header style. Before code select focused positive/two semantic controls,
full connections/launch/console regressions, host/harness/format/workflow/pin checks,
source freezing and all-attempt retention. Record image bounds and docs changes.
