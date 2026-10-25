# 0014: Bound repeated writers and late inherited readiness

Accepted 2026-09-05 for BG-040/BG-054, preserving decision 0003's first-frame
contract. A second write after acceptance must see EPIPE, without another
readiness transition or consumer launch. A nonblocking junk writer has explicit
byte/time limits; the reader consumes at most the remaining six-byte frame,
rejects its invalid prefix and closes. This is bounded pressure, not an unbounded
stress benchmark. Ignore SIGTERM in that fixture so pipe closure is observed
rather than inferred from process death.

A real forked helper inherits the launch readiness writer. The main process
waits for helper registration then exits. Establish the main's exit before
allowing the helper to write READY into the still-open pipe. The next adapter cut
must discard it and never launch the consumer. A subsequent helper write must
receive EPIPE. Handshakes establish each ordering; arbitrary sleeps do not.

The orphan helper has a ten-second self-watchdog and a cooperative release path
that closes its writer and records exit-path progress. The test reaps its direct
main process; external helper reaping is explicitly unobserved. Do not signal a
numeric orphan PID or claim crash containment. Cleanup always requests release.
Run an isolated terminal-priority mutation to verify the late-helper oracle.
No runtime/model or native contract change is selected by this test decision.
