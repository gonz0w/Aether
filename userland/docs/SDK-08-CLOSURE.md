# SDK-08 producer/consumer closure — UL-005

2026-09-07. Current result: the [matched producer run](evidence/sdk08-matched-2026-09-07/README.md)
passes bounded positive, exact memory-grant denial and positive reclaim checks.
Independent review and broader acceptance remain open. Denial native reclaim was
not demonstrated. The earlier selection-only record below is historical and is
superseded for current status; its checker remains a historical not-run control.

The selected retained UL-044 snapshot matches all 4557 hashes in the actual SDK
native receipt; its NATIVE-C hash is 81f802d1ae5fd0821ddd2664f22ecfa9acd46c9a02bc2efb810dcfb5bd4897ec.
The earlier a0b977... lead refers to a different native-memory snapshot. Neither
the missing lead nor live-tree drift requires using the live tree. Exact current
run/source/artifact identities are in the linked evidence.

## Historical selection-only checkpoint

## Consumer (selected)

Imported target `1b9c2fedc9cebba0785c4f4ec5157abaf580e886eae3cb8f809375a70062ab8e`
and libc receipt `f1d28e47b892ea8773afe0b48d9c6ba805dd012a1150222cfe7c939414b4bdb1`.
Probe is `experiments/native-c/io_probe.c` at the receipt `probe_sha256`, with
matching I/O and memory adapter hashes. Host ELF
`build/sdk-startup-lefmmlgo/startup.elf` hash
`d804589de3bf3f225d3ab301b5dadec0c8bbcc7e3890c1684e63e3cf4f908dbe`.
Native payload form is `AENATC01` || 32-byte bootstrap || ELF. Packing that
envelope is not a native run.

## Producer (not selected)

The 2026-09-05 `kernel_contract_sha256`
`a0b97740e7437d22cdebf07ad696c2aca903379914cfbba3e4dd10f655bd637a` is not in this
checkout. Live `aether/docs/NATIVE-C.md` is
`44d449dc325364c0b797e58789d98cefe0db15e430194c9a2572842fc26b9298` and is a moving
tree (~96G). It is not selected. sys-init
`scripts/build-native-supervisor.py` is recorded as a lead only.

A later SDK-08 run needs an isolated, hash-pinned producer snapshot whose
contract is explicitly reviewed. Do not execute against the live sibling.

## First intended cases (all NOT RUN)

pass (IO PASS + reclaim), one denial, cleanup. Not the full historical io suite.

Checker: `python3 -B experiments/sdk-consumer/check-sdk08-closure.py`.
