# Offline Aether serial-shell candidate

From this repository root, build the repaired ABI24/AENMX009 candidate and test
one shell through orderly shutdown:

```sh
python3 scripts/build-aether-session.py out/my-session --smoke immediate
```

Use `--smoke delayed` to wait 35 seconds at the first prompt and two seconds at
later prompts. Omit `--smoke` to build without boot acceptance. Output must be a
fresh directory under this repository's existing `out/`, without symlinks or
parent traversal. No root privileges are needed. The command does not fetch,
install or read sibling repositories. Released standards pins and the separate
[ABI22 baseline](AETHER-BASELINE.md) are unchanged.

The [recipe lock](aether-session.lock.json) freezes all current owner Rust/linker
sources, the sealed kernel/client/firmware archive and member metadata, the
producer workload/oracle, qualified ELF/raw identities and scoped stack review.
Every archive member is checked before staging. Only the normal image, payload
and kit are staged. Original kit notices are retained. The recipe rebuilds the
owner; it reuses the sealed kernel and client binaries. It does not claim a fresh
kernel, SDK, libc or shell build.

The recorded host is macOS arm64. Rust 1.98.0, xorriso 1.5.8.pl02 and QEMU 11.1.1
must already be present at the locked paths. `--tools paths.json` may relocate
identical executable bytes; use the same `rustc`, `xorriso`,
`qemu-system-x86_64` keys and `path`/`sha256` entries as the lock. Different hashes
are rejected. Rust uses its adjacent toolchain library directory. Other tools do
not inherit that library override. Executable identity does not freeze the
complete shared-library/sysroot closure. Other host qualification is deferred.

The rebuilt owner must equal both qualified raw and ELF bytes: 15,120 bytes of
code, with the scoped 3,816-byte stack inspection inside 4,088 usable bytes.
Exact equality permits inspection reuse; it is not a fresh independent formal
stack proof. The recipe replaces only the envelope's owner. It reads back all six
boot components and preserves exact client, spare and entropy bytes. ISO metadata
may vary; each new ISO gets its own hash. Inputs and tools are rechecked afterward.

Progress/errors use plain ASCII stderr. Stdout contains one result JSON; help
and version print text and exit 0. Exit codes are 0 success, 1 operational failure,
2 blocked input/output precondition, 64 invalid usage, 130 keyboard cancellation.
Each owned output retains `result.json`, phase logs, sources, kit and artifacts.
Smoke additionally retains `serial.log`, `qemu.stderr` and `smoke.json`. Failed
output stays in place; select a new directory for another attempt.

Smoke sends three exact commands in fragments after observed prompts. The
unchanged independent producer oracle requires exact 90 UART bytes, eight
admissions, ten terminal identities and reclaims, phase cleanup before later
prompts, and final owner-authorized halt. Shell PID/state, external helpers,
pipelines, redirection and stderr are checked. Guest exit, panic, timeout or tool
failure cannot count as success. Each tool has a 180-second/4 MiB bound; native
execution has 90 seconds, 1 MiB UART and 4 MiB stderr. Owned live groups are
terminated and children reaped on failure or interruption. Tools must not detach.

For an interactive development boot, `result.json` contains `console_argv` with
private firmware variables and serial stdio. Inspect that list, recheck the
recorded artifact and QEMU hashes against the lock, then execute the arguments
with your terminal's stdin connected. This manual boot has no smoke watchdog or
acceptance oracle. Reset `console-vars.fd` from verified `kit/vars.fd` before a
later boot. Type `exit` to select shutdown after confirmed shell settlement.
This is a raw serial development shell with finite SESSION quotas, no automatic
restart, login, general TTY/job control, persistence or production installation.

[Decision 0185](decisions/0185-offline-serial-session-recipe.md) records scope and
simpler alternatives. [Recipe evidence](evidence/serial-session-recipe-2026-10-04/README.md)
records fresh immediate/delayed consuming witnesses and local checks. The earlier
[EOF race repair](evidence/terminal-read-race-2026-10-04/README.md) retains before/
after and rejection controls; the exact first historical caller was not captured.
Remaining mismatch/exhaustion/uncertain-cleanup qualification and independent
assembled review stay open. Neither smoke nor manual boot is assembled-v1,
release or full POSIX acceptance. Trusted local tools retain host permissions;
no filesystem deadline, race-free confinement, fatal/repeated-signal handling,
network sandbox or complete toolchain closure is claimed.

The [acceptance matrix](SERIAL-SESSION-ACCEPTANCE.md) now records eight fresh
boot-handle/grant/final-action denials. They use private controls; this maintained
recipe still builds only the unchanged normal owner. Exhaustion, further cleanup
uncertainty, component-loader negatives and assembled review remain open.

Selected finite/cleanup/component/write denials are now qualified in the acceptance
matrix. Fifteen sequential helpers complete, but a sixteenth cannot be admitted
under the current matched profile. The [local lifetime handoff](SESSION-LIFETIME-HANDOFF.md)
records the continuing-use blocker. This recipe remains a bounded developer shell.
