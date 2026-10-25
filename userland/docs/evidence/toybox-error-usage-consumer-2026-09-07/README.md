# UL-067 local Toybox error and usage qualification

All31 native cases pass their specified oracles:11 error cases and20 usage cases.
Each non-mutant case verifies client/backend terminal results in two generations,
exact owner-checked bytes/positions and supervisor100/reclaimed4. Deliberate mutants
require exact rejection context with zero reclaims; those are not recovery claims.

| Profile | Local native evidence |
| --- | --- |
| Read/write EIO and EINTR | Status1 and exact upstream diagnostics. Read failure preserves16 input/output bytes; write failure32 input/16 output. No copy retry after error. |
| Malformed/cut read/write replies | Status1; exact committed prefix; shared poison prevents subsequent channel traffic, including attempted diagnostics and local retirement. |
| Error mutants | Wrong diagnostic rejects1505; false success rejects1501. |
| Extra arguments | `-`, `-u`, `-v`, filename, help, version, unknown option and empty argument reject64 before Toybox initialization; no input reads or stdout bytes. Short diagnostic writes preserve the full message. |
| Diagnostic failures | EIO/EINTR and malformed/cut replies preserve64 and the exact16-byte prefix. Unknown completion permits no later channel traffic. |
| Usage cleanup | Consumed input-close EIO retains64; no-memory-grant rejection also passes. |
| Usage mutants | Input read, corrupt diagnostic, false success and omitted close reject1520/1505/1501/1503 respectively. |

[Error receipt](errors/results.json) contains95 owned commands, including source
rebuilding the11 selected supervisors with the applet-specific accounting profile.
[Usage receipt](usage/results.json) contains138 owned commands. All233 process
receipts report complete cleanup. Each suite also runs the normal-copy regression.
All baseline applet objects, native adapter and per-case stdio/finalization objects
are rebuilt. SDK/CRT and backend remain verified dependencies; usage supervisors
are verified payload reuse. This does not qualify a complete producer rebuild.

## Provenance and reproduction

The runtime/SDK inputs are the unchanged [normal-copy snapshot](../toybox-native-consumer-2026-09-07/README.md).
[Additional inputs](error-usage-inputs.json) bind producer recipes and the Rust
command receipt, checked against their producer manifests before copying. The
local driver now selects cat/errors/usage and resolves Rust from the existing
host lock, rather than ambient rustup. No source/oracle was weakened. It records
each adapted recipe and execution identity in a separate directory. The original
recipe, native source, tool, argv, environment, payload/ELF/ISO and raw-log identities
are retained. No failed attempt occurred in this continuation.

```
python3 -B experiments/toybox-native/run.py --snapshot build/toybox-consumer-x__smsdx --profile errors
python3 -B experiments/toybox-native/run.py --snapshot build/toybox-consumer-x__smsdx --profile usage
```

Commands use the existing owned process helper, clean environment and180-second
limit. Pinned native_smoke retains its30-second watchdog and terminate/wait cleanup.
Build outputs remain in the recorded private snapshot; no installation, network
fetch, sibling edit or pin change occurs. See [plan](PLAN.md) and [driver](run.py).

## Change review and next gate

UL-067 CAT-03/05 now have local bounded witnesses. Codex reviewed the source owner
prefix/diagnostic expectations, no-input usage path, preserved64, once-only local
alias consumption and poison behavior against the retained code. Complete EIO
close confirms consumption while other roles remain usable; unknown close poisons
and local retirement does not establish remote acknowledgement. Independent owner
checks and four reclaims remain authoritative. Foundations O/I/E, quality CP/TD/TE,
existing upstream C flags and licenses apply. ASCII output and smoke markers are
unchanged. Independent reader/maintainer review remains pending.

CAT-06 finalization, full producer/regression qualification and broader CAT review
remain open. A [new producer finalizer plan](finalizer-producer-plan.md) addresses
callback-generated buffered output, flush errors, close failures and private-hook
re-entry; [observation](finalizer-lead.json) found no completed manifest, archive
or native receipt. It is a research lead only; no newer runtime bytes were consumed.
Next intake must verify its completed source/evidence pair and assess the final
close-error diagnostic requirement. Recursive/signal finalization is still separate.
UL-067 and M3 remain active; optional tuning stays deferred.
