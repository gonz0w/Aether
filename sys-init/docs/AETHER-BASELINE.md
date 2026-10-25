# Offline Aether developer baseline

From the repository root, build the frozen AENSI001/ABI22 composition and boot
one useful command cycle followed by orderly halt:

```sh
python3 scripts/build-aether-baseline.py out/my-baseline \
  --dependencies out/si07-loop/.deps --smoke
```

The output must be new, below this repository's `out/`, with an existing parent
and no symlink or parent-traversal components. No root privileges are needed.
Omit `--smoke` for a build only. The result is a developer image, not an installed
init product or a release. This recipe does not read mutable sibling repositories.

## Inputs and setup

[The local recipe lock](aether-baseline.lock.json) pins the retained kernel source
archive, source membership, three payloads in the envelope, startup record,
maintained sys-init owner modules and five tool executables. It is an experimental
composition pin; released standards pins are unchanged. Dependencies must already
exist locally and match every hash and length in the retained
[dependency manifest](evidence/si07-loop-2026-10-03/dependencies.json). The example
uses the existing verified experiment cache; the recipe copies verified bytes
into its own output. Another directory containing exactly those files is valid.
Missing files or changed identities block the build before staging. Provisioning
or downloading dependencies is a separate task; this command does neither.

The recorded host is macOS arm64, with Rust 1.98.0, Zig 0.16.0, QEMU 11.1.1,
xorriso 1.5.8.pl02 and Python 3.14.7. Tool paths are local defaults. To relocate
identical executables, supply `--tools paths.json`, a JSON object with the same
`rustc`, `zig`, `qemu`, `xorriso`, `python` keys and `{ "path": "...",
"sha256": "..." }` entries as the lock. Different executable hashes are rejected.
Rust uses its adjacent toolchain library directory; Zig and QEMU do not inherit
that Rust library override. This records executable identity, not complete
shared-library/sysroot closure. Other host platforms are not qualified here.

## Results, failures and console

Progress goes to stderr; success prints the result JSON to stdout. `result.json`
retains commands, status, artifact hashes and stack-inspection provenance. Each
build phase retains a bounded log. `--smoke` also retains `serial.log`, `qemu.log`
and `smoke.json`. Exit codes: success 0, operational failure 1, blocked input or
output precondition 2, invalid usage 64, keyboard interruption 130. Help/version
print to stdout and exit 0. Failed output is retained; choose a new directory for
the next attempt. Never reuse or delete another invocation's output implicitly.

The build requires raw owner and linked ELF bytes to equal the tested baseline.
The owner is 10,152 bytes within the 16 KiB bound. Identical linked bytes permit
reuse of the scoped 2,696-byte stack inspection within 4,088 usable bytes; this
is not a new independent whole-program stack proof. ISO timestamps may differ;
each produced ISO gets its own digest. Build-only success is not native acceptance.

The automated smoke boots QEMU with one emulated core, 256 MiB, no NIC and private
firmware variables. It sends `r` at the first request boundary and `h` at the
next. The developer console permits `r` to run bytecount and `h` to halt between
cycles, including before the first command. The existing startup test probe
idles for about 30 seconds; this is not product boot-time policy or a performance
measurement. Exact ordered terminal statuses 0/0/17, one completion, three reclaims
and the recorded idle/halt bounds are required. This is a fixed-memory backend,
not an interactive shell, authenticated operator console or persistence system.
Command epochs are finite; this recipe does not prove indefinite uptime.

Build phases have 180-second/4 MiB tool bounds; the guest has a 90-second deadline
and 4 MiB serial bound. Owned child process groups are stopped on failure or
interruption. Local trusted tools run with host permissions: offline inputs and
NIC removal do not claim a host network sandbox, filesystem deadlines, race-free
confinement or full dependency closure.

## Coverage and next work

[Recipe evidence](evidence/abi22-baseline-recipe-2026-10-03/README.md) records fresh
native acceptance and input/output failure controls. The larger existing
[SI-07 disposition](SI07-DISPOSITION.md) retains protocol gaps and release limits.
The explicit service-table profile below separates the startup test probe.
Bounded supervision and an explicitly matched usable environment follow.
ABI17 Dash and ABI23 interactive userland are separate profiles; their payloads
cannot be substituted into this ABI22 recipe without a matching composition.

## Explicit service-table profile

```sh
python3 scripts/build-aether-baseline.py out/my-table \
  --dependencies out/si07-loop/.deps --service-table --smoke
```

`--service-table` selects the locally qualified AENSI001/ABI22/service-table
composition. The default continues the exact previous baseline and its idle/grant
startup probe. The table profile skips that test probe; it retains command/output
assertions and fail-closed behavior. It is still a developer workload.

The [constant data table](../prototypes/native-command/service_table.rs) lists
Backend (image/slot1, order0), Runner (image/slot0, order1), Command (image/slot2,
order2). The compiler rejects missing/duplicate roles, mismatched image/order and
nonzero automatic retries. This one topology is supported by the existing command
protocol; arbitrary reordering or payload substitution needs matching code and
fresh evidence. Table data does not grant authority. Actual launch uses the
kernel-provided image grants and paired owner. Epochs and completed command reuse
remain bounded; automatic retry remains zero until supervision is implemented.

Edit this inspectable table as a source change, review compatibility, rebuild and
qualify the composition, then update the experimental local recipe lock. No runtime
parser, package descriptor or configuration file installation is introduced. The
new owner is 9,984 bytes, with scoped inspected stack 2,712/4,088 usable. Its raw/ELF
identity is separately pinned; the default retains 10,152 bytes and prior identity.
[Decision and limits](decisions/0179-abi22-inert-service-table.md) and
[retained evidence](evidence/service-table-2026-10-03/README.md) describe the two
native witnesses. Tick observations are test results, not boot-time benchmarks.
The next work is bounded supervision on this one useful path.

## Bounded supervised profile

```sh
python3 scripts/build-aether-baseline.py out/my-supervised \
  --dependencies out/si07-loop/.deps --service-table --supervised --smoke
```

This explicit profile allows one automatic command replacement only before any
command backend read or write. Command failure must have an observed terminal,
settled logical references and complete cleanup/reclaim of all three roles before
a fresh cohort starts under a new epoch. Backend/runner automatic retries remain
zero. Read activity alone disqualifies replay. Unknown transport/cleanup stops
admission; it does not reach the retry branch. This is safe only for the frozen
command's mediated effects, not arbitrary executables, devices or outside effects.

Two failed attempts exhaust one request's retry budget. Exhaustion or failure
after I/O enters a distinct failed state. `r` cannot admit more workers there;
`h` permits orderly halt after known cleanup. Failed requests do not emit the
successful completion marker. A successful request returns to the normal boundary
with a fresh budget for the next request; finite epochs remain a separate limit.
Unknown cleanup retains ownership and terminates the fixture without claiming halt
or recovery. Partial startup and malformed transport still use fail-closed fixture
behavior; this is not general production recovery or full init acceptance.

The experimental lock separately pins the supervised owner (11,080 bytes) and
scoped stack inspection (2,744/4,088 usable). Baseline and table-only builds use
their exact pinned module snapshots under compatibility_sources; current maintained
owner modules feed supervision. Both older owner/ELF/envelope identities reproduce
exactly. A new current source hash does not silently revise their accepted images.

[Decision](decisions/0180-abi22-bounded-pre-effect-retry.md) and
[evidence](evidence/supervised-retry-2026-10-03/README.md) retain five fresh native
cases, failed intermediate attempts, compiler controls and scoped resource review.
The next product step is an explicitly matching usable environment composition;
ABI17 script and ABI23 interactive payloads remain separate integration boundaries.
