# UL-007 native SDK link preflight — 2026-09-07

PASS for linking only; native dash execution **NOT RUN**. The unchanged pinned
Linux-reference dash 0.5.13.5 objects link with the captured native SDK, CRT and
existing native memory/startup-I/O adapter. The resulting static x86-64 ET_EXEC is
241272 bytes with 54 distinct LOAD pages, no unresolved external symbols, no
interpreter/dynamic segment and no writable/executable LOAD segment. Page count
is not a runtime memory requirement or loader acceptance claim.

Run: `python3 -B experiments/dash-native/link.py`. Private output:
`build/dash-native-link-szk3m4f7`. All five owned commands completed successfully
with cleanup, each bounded at 180 seconds. No failed attempt in this preflight.
[Results](results.json) retain exact argv, tool/input identities and artifact hash;
raw streams, process receipts, map, ELF and full disassembly are retained here.
The driver verifies all reference objects, captured snapshot files and 231 SDK
files before consuming them. Existing generated Linux configuration is reused;
this is not a fresh source build or native shell configuration qualification.

## Concrete ABI findings

[Selected symbol bodies](selected-disassembly.txt) show native `int $0x81`
transport, including getpid `0x10027`, getuid `0x10066`, vfork `0x1003a` and execve
`0x1003b`. In the captured [dispatcher](native_c.zig), these operations match
neither the routed service ranges nor supported startup calls and reach the
`else => result(s, -38)` fallback. This is a source/disassembly assessment, not an
observed native invocation. Native threads and service-owned launch facilities
exist separately; they do not supply these linked POSIX call semantics.

Retained dash main.c calls getpid before init/procargs. Signal setup also needs
explicit qualification: upstream trap.c can hide failed sigaction operations,
so a successful builtin command alone would not qualify shell startup. Missing
process, descriptor and signal semantics must not be replaced with success stubs.
See [the next integration sequence](../../NATIVE-DASH-GAPS.md#native-sdk-preflight-and-next-integration-ul-007).

The reference receipts and COPYING are preserved. Archive hash is a content pin,
not source authentication. UL-016 retains source trust and generator/output
licensing review. Independent technical/reader review remains pending; UL-007
and M3 remain active. SHA256SUMS records this retained packet.
