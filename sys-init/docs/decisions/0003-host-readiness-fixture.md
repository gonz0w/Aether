# 0003: Tighten the trusted host readiness fixture

Accepted 2026-09-05 for the existing private-root, trusted-child experiment only. This records the contract before extending its readiness tests. It does not retroactively turn the initial host slice into a reviewed production runtime.

Scope: portions of BG-040/BG-028/BG-054. Producer is the foreground fixture child; consumer and direct-parent observer is HostRuntime. Foundations O-02–O-04, I-01/I-04/I-05 and E-03/E-06 apply through [offline adoption](../STANDARDS.md). Shared standards, pins and native ABI remain unchanged; this is a sys-init-owned adapter contract.

## Frame and authority

Retain the existing six-byte `READY\n` first-frame contract and `AETHER_READY_FD` environment key. A bare newline is simpler and familiar from s6 research, but would change the existing fixture. A larger versioned message adds no current consumer value; the host profile already scopes the interpretation. Compatibility with s6 or sd_notify is not claimed.

Read at most the bytes remaining in that six-byte first frame. A matching partial prefix waits within the startup deadline; a mismatching prefix or EOF before completion rejects readiness and requests child termination. Once all six bytes match, accept once and close the channel. Bytes after the first frame are not parsed; a producer writing later must tolerate a closed reader. Acceptance must not depend on whether the pipe returns six bytes or coalesces trailing bytes into a larger read.

Each generation receives a new pipe. The parent closes its write end after spawning and passes only the intended readiness descriptor with other descriptors closed. Descriptor possession is delegated authority: a helper that inherits it can signal. This is not main-PID authentication or arbitrary descendant containment. Trusted fixture helpers must be explicitly owned/reaped by their parent; native transfer/revocation remains outside scope.

Python's primary [subprocess documentation](https://docs.python.org/3/library/subprocess.html) describes pass_fds/close_fds, child polling/waiting and POSIX signal return values; [os.read](https://docs.python.org/3/library/os.html#os.read) reads up to the requested byte count. Reviewed 2026-09-05. These support the adapter mechanism, not cross-platform test evidence. A persistent direct parent preserves child observation; an unrelated helper cannot replace its wait ownership.

## Ordering, bounds and cleanup

Poll terminal state before consuming that child's readiness. Known terminal outcome discards pending readiness; no claim is made about exits occurring after the observation cut. The model still decides generation/deadline/admission ordering. At most six bytes per readiness buffer and four observations per model cut; existing runtime/event budgets remain in force. Invalid readiness is a stop request, not a terminal result. Reclaim closes the reader and reaps the actual child. close() is emergency cleanup only for the adapter's tracked direct children.

Validation must cover fragmented delivery, coalesced trailing data, early EOF, mismatching partial prefixes, unrelated inheritable descriptors, known exit with buffered readiness, normal stop/reap and existing generation/retry cases. Use real pipes/children; a read-size wrapper may force fragmentation without sleep-based synchronization. Capture exact source hashes and test count. Native, Linux/BSD/illumos execution, parent-death containment and authenticated control IPC remain untested or pending.
