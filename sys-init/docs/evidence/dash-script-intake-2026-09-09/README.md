# Bounded Dash script intake

2026-09-09. Three fresh local replays pass: actual sh hello.sh and both existing
missing-root/missing-close controls. This is producer-image consumption, not a
sys-init-owned shell, full shell acceptance, source rebuild or sustained boot.

The producer manifest and every219 source/7486 target-archive file hash verify.
Both archives reject duplicate/unlisted/unsafe paths and non-regular entries in
this intake. Exact archive/manifest identities and selected members are retained
in intake.json. All producer packet files except the1.2 GiB target archive are
copied under producer/. Its hash and complete target inventory are retained; the
three selected envelopes/logs are local, and the three verified ISOs remain under
out/dash-script-intake. This is intentionally a selected artifact intake, not a
self-contained copy of every producer target. Preserve original notices.

Replay uses our existing qualified native_smoke/dependency/emulator scripts,
after exact byte comparison against the new frozen sources and boot dependency
lock. The pinned QEMU executable hash is checked before launch; its version and
firmware dependency hashes are checked by the helper. Each child run has45-second
outer and30-second guest bounds with owned terminate/wait cleanup. No build or
runtime follows a mutable sibling checkout. Exact commands, ISO hashes and
terminal/result lines are in replay.json; old producer logs remain separate.

- Script: exact in-image hello-newline output, actual file open/read/alias close,
  no live file records; shell0/stream17/file17 twice, supervisor100/reclaimed6.
- Missing root: shell2 and owner1501/reclaimed0 expected profile rejection.
- Missing close: shell0 but owner1599/reclaimed0 expected live-record rejection.

Full serial terminal/result sequences match the captured originals. The console
hello output is an in-image protocol/readback assertion, not fabricated host
stdout. Negative outcomes prove rejection, not recovered cleanup. No producer
369-case/M4 suite or matching userland acceptance is claimed as rerun here.

The [integration review](../../DASH-SCRIPT-ADAPTER.md) records the role/profile and
EOF differences, current coverage, limits and next local owner adaptation. Existing
sys-init runtime/standards pins remain unchanged. Full local checks follow;
sha256.json seals retained files excluding only itself.

Final validation: all ten local gates pass in run-42ha8k2u with checked sources
unchanged. All three released locks match prior hashes; git diff --check passes.
The three native replays pass, with no failed attempt. Source adaptation and
a sys-init-owned shell witness remain next; no broader acceptance is inferred.
