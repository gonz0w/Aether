# Simple service owner — 2026-09-07

BG-064 host/native acceptance. Final reports, source snapshots, compatibility
builds and unsuccessful attempts are retained here. This is a reusable component,
not a complete init, shell boot or recovery implementation.

All ten repository gates pass in run-sq7s5qdr, with checked inputs unchanged.
The required Rust suite passes eleven methods and twelve named check records,
including six owner tests and three private omission controls. host-final/ retains
source, commands and logs; rebuildable host executables are omitted.
owner-targeted-v1-2/ retains three fresh native cases, source/producer inputs,
raw/envelope/serial/QEMU records and ISO digests (ISOs remain in private out/).
Compatibility retains all 587 unchanged prior ABI16/15/6 images and commands.
The initial worker selection failure, compatibility-driver path failure, old
aggregate-count failure, and passing aggregate with a failed internal receipt
are retained separately. None of these unsuccessful attempts is acceptance.
Final teardown checks the exact receipt set and makes inconsistency fail unittest.

adoption/ captures the final references and BG-065 handoff. Shared locks,
producer/worker and catalog pins stay unchanged. tool-identities.json matches
previous qualified tool bytes. sha256.json seals every retained bundle file.
