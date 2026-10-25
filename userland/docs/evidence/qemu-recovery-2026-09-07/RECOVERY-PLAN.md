# UL-069 explicit recovery review

Requirement: measure recovery after the unchanged GNU main stty script separately
from its natural-restoration failure. Linux reference only; no native acceptance.
Foundations O/I/E and quality CP/TD/TE apply. Python 3.10+ standard library,
BSD-2-Clause original source; retain upstream GPL and runtime notices.

Reuse the approved consumer input receipt, checking every staged byte, and the
unchanged owned process/container helpers. Read-only inputs; private owned PTYs;
network/capabilities disabled, uid65534, 512 MiB, 32 PIDs, 120-second container.
Each child is the owned session leader, opens only the supplied PTY, attaches it
as controlling stdin and execs the existing GNU script or a local fault fixture.
No changes to upstream, emulator or user terminal. Parent owns both endpoints.

Four cases: real main script (45s, exit0, natural restoration false), changed
termios/window then exit23, same mutation then timeout (2s), and omitted-recovery
negative control. Exact termios and window comparisons must detect unrecovered
state; finally restores both and independently reads them back before closing.
The timeout process record must retain failure=timeout and complete=false,
with cleanup=complete. A witnessed expected failure is not a successful command.
No process timeout/no-op result may be relabeled as restored without measurement.

Capture command records/output, before/natural/explicit/rescue states, descriptor
closure, image/runtime/input hashes and every attempt. Main natural oracle remains
false even when explicit recovery passes. Scope excludes owner SIGKILL, detached
hostile descendants, restoration syscall failure and native recovery. Run syntax,
actual four-case guest and quality gate. Technical and reader review of this new
slice pending; approval of consumer adapters does not cover new recovery behavior.
Update README, quality inventory, STATE and BACKLOG with measured results and gaps.
