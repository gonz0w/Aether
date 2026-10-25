# R1-01 native serial transport evidence

The fifth console attempt passes actual bidirectional QEMU stdio exchange. This
is an experimental BSP transport grant, not a shell, TTY or first-release image.
The [contract](../../NATIVE-CONSOLE.md) defines authority, limits and open work.

| Attempt | Outcome / triage |
| --- | --- |
| console-uhilz7te | Build failure: Rust opt-level=2 exceeded the unchanged 4096-byte owner limit. Size optimization/LTO produces 1334 bytes. No target ran. |
| console-1y4t2quu | Target failure: invalid supervised ELF. Harness initially retained only the panic prefix; corrected to wait for its complete line. |
| console-n3g_6st0 | Target failure: full panic confirms invalid supervised ELF. Minimal worker lacked the existing loader's required TLS segment. |
| console-mfksdh3p | Target failure: zero-only TLS landed outside the accepted load-segment extent. Initialized TLS corrects the fixture layout; loader unchanged. |
| console-pqinry58 | Pass: real binary exchange and exact echoed bytes, worker authority denial across three generations, buffer/size/overflow checks, nonblocking empty RX, bounded short writes, permanent close. Wrong-input run fails specifically at supervisor result 901/reclaimed 3 and native profile rejection. |

Each attempt contains its original results.json and artifacts archive (including
logs, envelope, ELF and any generated ISO), plus source bytes verified against
every digest in its original receipt. Earlier source variants were reconstructed
from the scoped edits and checked byte-for-byte against those recorded hashes.
No failed attempt or loader constraint was discarded. Final source identities
match both regression suites. Raw echo logs contain NUL, ESC and CR deliberately;
view as binary data rather than trusted terminal presentation.

Additional final-source coverage:

- regression-d3p896os: seven existing M4 target cases pass, including semantic
  failures and the expected display pixel mismatch control.
- channel-suite-bjyx18fo: four native channel cases pass, preserving the previous
  bootstrap ABI/profile and supervised task paths.
- console-regressions-2026-09-06: final host tests (85 Python cases plus kernel
  tests), all offline standards/workflow checks and scoped Zig/Rust/C formatting
  pass. The earlier host and explicit Experience checks also pass.

Commands and UTC intervals are in console/host receipts. Existing regression
harness reports retain their native command/hash formats; their wrapper did not
record full UTC intervals, so this is not complete Testing-profile adoption.
Console receipts bind the supplied strict SDK archive/receipt and tool lock;
tools.json additionally records locally observed executable identity after runs,
not continuous tool attestation. Runs froze runtime sources; no consumer pin or
sibling repository was changed. Tools and sources are local working-tree inputs,
not an independently reproduced committed release.

Console command:

```sh
python3 scripts/console_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
```

Remaining coverage: injected UART line errors, forced TX exhaustion, lossless
paste/interrupt buffering, independent consumer adoption, physical hardware,
terminal modes and separate normal/diagnostic streams. The bootstrap owner holds
the current duplex grant; delegating it to a separate console service requires an
explicit lifetime/ownership extension. No package, filesystem or shell acceptance
follows from these transport checks. Retain all attempts under DEVELOPMENT policy.
