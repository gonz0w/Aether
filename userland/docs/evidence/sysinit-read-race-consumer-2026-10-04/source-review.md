# Scoped technical review — UL-007/012

Implementation-agent review, 2026-10-04; independent SSDK-06 reader pending.
The frozen repair.diff and maintained-final dispatcher were read with terminal(),
reclaim(), poll() and init entry. On read0 the same existing peer handle is
reobserved. A running peer fails check; native status must pass existing translation
and child/pipeline identity validation before cached frame/standard state clears.
Reclaim still requires terminal plus collected for children, exact endpoint closure,
owned task release and stale EBADF. Uncollected terminal children remain on the
existing wait/result delivery path. The fresh mutable frame borrow follows the
terminal call; no held mutable alias, new state, grant or unsafe operation appears.
The write branch retains its previous check; this intake does not qualify EPIPE.

Producer inspection is scoped evidence:15120 code bytes and3816 estimated stack,
34 immutable builtin sites; no local owner compilation or whole compiler/SDK audit.
Actual local objcopy verifies raw/ELF equality for all five selected owners.
All source and inspection bytes are frozen in the verified full producer packet.

The positive oracle is unchanged userland code. The negative identity/UART algorithm
is borrowed verbatim from the reviewed producer check (BSD-2-Clause), adapted only
for local source/receipt paths and complete exact fault/panic suffix. It checks
all three complete host writes, actual EOF/EBADF diagnostics at frozen source lines,
exact preceding terminal/admission identities and UART prefix. Host writes alone
do not prove all guest reads. Live EOF is explicitly a synthetic value control;
the yielded old-owner read0 witness uses the real kernel. Fifteen corruptions test
that positive/negative checks reject missing evidence and false completion.

Local process helper remains unchanged and pinned. Interactive emulator inherits
the outer owned driver process group; explicit termination/kill/reap is bounded,
with separate flash variables per case. The maintained builder rebuilds clients
from the frozen SDK and checks exact ISO components before kit publication. Output
and retention stay in owned build roots; prior evidence and sibling files unchanged.

Final capture correction: borrowed driver initially lacked its stated4MiB stderr
file-size check. It now checks that bound each collection loop. Initial passing
cases remain separate; final six native witnesses use the corrected source.
