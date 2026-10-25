# Imported SDK consumer evidence — UL-005

Independent verification passes for the returned pinned SDK descriptor, target,
all four hashed tables, exact blobs, 235 package file hashes, modes and sizes,
and matching imported/recovered package records and payload sets. verification.json
binds the owner receipt and package identity. verify-imported.py captures the
one-shot read-only check; it is not a new package import/validation interface.
Owner denials and publication/recovery execution were inspected, not rerun.

The first imported consumer attempt passes in build/sdk-consumer-uw9o9dqg. It
copies all 231 SDK inputs from the actual imported root after verification and
records the package binding in summary.json. Strict C17 compilation and explicit
static libc linking pass. Missing SDK headers and omitted libc fail with exact
expected diagnostics and absent outputs. ELF64 x86-64 inspection finds no
undefined symbols, interpreter or dynamic segment. Every process cleans up.
The captured driver, argv/environment, tool/source hashes and raw streams are in
the attempt directory. No artifact was executed and no sibling files changed.

This independently corroborates SDK-01/02 payload transport for the selected
package and supplies the leaf-function link subset of SDK-05. It does not qualify
C startup, external I/O/memory adapters, compiler helpers, static rebuild tracking
or native execution (SDK-07/08). Unknown historical host fields remain explicit.
UL-005 remains active. Source authenticity and independent review remain open.
