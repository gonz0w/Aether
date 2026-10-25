# 0009: Own the abnormal-terminal worker probe in sys-init

Accepted 2026-09-05 for BG-032/BG-040. Reuse the frozen BG-055 kernel and musl I/O
SDK. No companion source, syscall, native ABI or shared pin changes are required.
This C worker and Rust policy are test fixtures, not a production language choice.

The worker writes distinct generation-tagged bytes to stdout/stderr, then signals
readiness without closing either output. It waits for one input byte: F executes
an actual x86 UD2 fault; X exits normally. The supervisor can instead stop it via
the existing instance operation. A bounded yield loop is a fixture limit, not a
new service-clock contract. Stream errors or unexpected commands fail the worker.

Run two independent two-generation traces: explicit stop then normal exit, and
actual fault then normal exit. Before termination, exact output must be retained
and its next offset must return EAGAIN. After termination, verify terminal kind
and detail, historical readiness, the same output bytes followed by EOF, rejected
input/seal, explicit reclaim and stale-handle denial. A fresh handle must expose
generation-two bytes rather than generation-one output, then complete normally.

Compile only the local worker against a trusted verified SDK, recording source,
headers, startup objects, native I/O object, libc, tool hashes and commands before
consumption and checking them after. The SDK build receipt binds its producer
build; these additional pins identify the actual link inputs. This is not hostile
filesystem protection or publisher authentication. Retain static ELF inspection
and native execution separately. Existing SDK descriptors and code remain intact.

A wrong-fault-kind policy must reject at its intended assertion; omitted backing
zeroing must reject independently. Retain a correct pass for both terminal paths
and recheck original client compatibility. No supervisor recovery, graceful POSIX
signal delivery, SMP, general process service or production console is claimed.
