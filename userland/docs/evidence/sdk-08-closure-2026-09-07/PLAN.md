# SDK-08 producer/consumer closure selection

Select the exact imported-SDK consumer and native producer identities for a later
execution run. Do not execute ELF, copy the live Aether tree, edit siblings or
change pins. Historical 2026-09-05 kernel_contract_sha256 is absent from this
checkout; live NATIVE-C.md has drifted. Native status stays NOT RUN.

Consumer: receipt-pinned io_probe.c, native_io.c, native_memory.c, memory_probe.c
and imported SDK libc/crt objects; host ELF from sdk-startup-lefmmlgo
(artifact_sha256). Envelope form is AENATC01 plus 32-byte bootstrap plus ELF;
packing is not execution.

Producer: isolated snapshot required. Live /Users/cam/DEV/aether is a moving tree
and is not selected. sys-init build-native-supervisor.py identity is recorded as
a lead, not a pin.

Intended first native cases after a captured snapshot: pass, one denial, reclaim
cleanup. Full test_io.py matrix is not this slice.

Command: python3 -B experiments/sdk-consumer/check-sdk08-closure.py
Help/version/usage 0/0/64. Mutants: native pass without snapshot, wrong ELF hash,
equating live contract to the historical pin. Quality gate. Independent review
and SDK-08 execution remain open.
