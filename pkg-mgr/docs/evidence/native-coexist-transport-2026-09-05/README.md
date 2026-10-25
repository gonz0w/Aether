# UL-047 coexistence package transport — 2026-09-05

Twelve rebuilt-image QEMU outcomes pass: six independent ABI-7 coexistence cases
and six fresh ABI-5 broker regressions. Host: arm64 macOS; target: Aether x86-64.
The source and contracts are from accepted captured inputs; no moving sibling
implementation, immutable standard or shared ABI was edited.

`invocations.json` records both exact harness commands, external evidence/tool
pins and captured source roots. Original reports are the summary.json and
abi5-regression/summary.json beneath
`/Users/cam/DEV/Aether-userland/docs/evidence/native-coexist-userland-2026-09-05`.
Normalized copies here preserve report data; original bytes are externally pinned.
The producer archive/source identities and consumer build records remain in those
reports. Matching captured trees are native-coexist-userland-facbg_76/Aether and
native-broker-userland-722hyd56/Aether beneath Aether-userland/build.

Private roots retain large images, staged payloads and copied tools/dependencies:

- `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul047-coexist-2026-09-05`
- `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul047-abi5-2026-09-05`

Small results, receipts, serial logs, commands and tool inventories are copied here
and hash-checked. Result records bind the package helper closure; source copies
preserve this harness/transport. Reproduction requires original pinned inputs and
a fresh --root. Never overwrite a published destination to rerun a witness.

Coexist positives require both backend generations exiting 17, requester 29 and
three reclaims. Repeat-collect/partial-request/requester-exit/small-pool/wrong-data
require requester 66/41/42/59/78. Broker 903 must follow one reclaim for partial
request/small pool, two for the others, then the exact rejection panic. Timeout
and unrelated failures cannot pass. ABI-5 retains its original worker 17/33 and
independent negative details.

The reduced-pool image uses the separately declared coexist-small-pool receipt,
not normal coexist configuration. Five input controls reject wrong schema/profile,
incomplete cases, missing small-pool selection and pool selection on the positive
case before output creation. Results are in input-controls.json. Ordinary fixtures
also reject missing/integer/incorrect pool options and receipt relabeling.

This establishes bounded raw file RPC coexistence, not FD/stdio use through the
broker, inherited open-file ownership, exec/fork, shell, persistence or sys-init
composition. ABI-8/9 capacity needs its own independent witness. These twelve
outcomes overlap earlier ABI-5 coverage; do not count them as twelve new features.
[Contract](../../NATIVE-LAUNCH-TRANSPORT.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary fixture scripts passing after this change.
